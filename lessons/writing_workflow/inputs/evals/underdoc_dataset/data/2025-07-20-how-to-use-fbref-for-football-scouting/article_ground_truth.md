# How to Use FBRef for Football Scouting with Python?

*Using a Free Resource to Recruit Players*

If you google: “football data” or “football statistics” you’ll probably see FBRef as one of the firsts websites that offer free statistics.

It is one of the best places to start when you don’t have access to paid providers and want to build your own players profiles for scouting, you can leverage this data and **flag** specific players from different leagues.

This gives you the opportunity to filter players and then check through video that the player you selected actually meets your criteria in the context of the team your scouting for.

Metrics you can find here:

- Attacking stats: passing accuracy, possession,

- Defensive stats: tackles, blocks, interceptions, clearances, errors.

- Goal and Shot-creation actions.

- A basic Scouting report compared with other players from similar leagues.

This can give you an idea of the player performance from a given season.

I’ll show you how I scraped data from Championship, League One, and League Two to find a hypothetical signing for Sheffield United.

I also integrated the FBRef data with the Transfermarkt data, a process I described in my last post:

[**How to Scrape Transfermarkt with Python: Data-Driven Player Recruitment using England’s Championship, League Two, and League One data.**](https://ricardoheredia.substack.com/p/how-to-scrape-transfermarkt-with)

[Ricardo Heredia](https://substack.com/profile/313134153-ricardo-heredia)

·

July 9, 2025

[Read full story](https://ricardoheredia.substack.com/p/how-to-scrape-transfermarkt-with)

### My Approach for Scraping FBRef

I basically did a two-step process: manual then automatic using only the _requests_, _pandas,_ and _pyjanitor_ packages.

1. First, I manually checked the page of the Championship league for the 2024–2025 season and went tab to tab to get familiar with the metrics I actually needed (they’re a lot, and most of the time you don’t need that many). I did this for this league since it basically has the same metrics as League One and League Two.

Since I was interested on midfielders and forwards I only used data from all of the tabs except Goalkeepers.

2\. Web scraping: to do this I need to to look at the HTML and tried to find the tabs I wanted to obtain data from. You do this by opening the FBRef URL in Chrome and righ-clicking “Inspect”, to check the HTML code. Then, you get this beautiful Matrix-like mess.

The idea is to obtain the information from a table like this:

I used this function for that:

```
def get_clean_table(url, table_id):
    """
    Fetches and cleans a table from fbref.com given a URL and a table ID.

    Args:
        url (str): The URL of the webpage containing the table.
        table_id (str): The 'id' attribute of the HTML table.

    Returns:
        pd.DataFrame: The cleaned and ready-to-use DataFrame.
    """
    # Make the request and get the HTML content
    response = requests.get(url)
    html = response.text.replace('<!--', '').replace('-->', '')

    # Read the specific HTML table
    df = pd.read_html(html, attrs={'id': table_id})[0]

    # Clean the columns with clean_columns from pyjanitor
    # It converts the name of the columns as lower case
    df = clean_columns(df)

    # Fill missing values and reset the index
    df = df.fillna(0).reset_index(drop=True)

    return df
```

I then used this other function for some data cleaning regarding mutlti-index and columns names so I could get a decent result:

```
def clean_columns(df):
    """
    Cleans and flattens the columns of a DataFrame with multi-level indices.

    Args:
        df (pd.DataFrame): The original DataFrame with multi-level column indices.

    Returns:
        pd.DataFrame: The DataFrame with flattened and cleaned columns.
    """
    # Flatten the columns by joining the levels
    df.columns = [' '.join(col).strip() if isinstance(col, tuple) else col for col in df.columns]

    # Rename the columns if necessary
    new_columns = []
    for col in df.columns:
        if 'level_0' in col:
            new_col = col.split()[-1]
        else:
            new_col = col
        new_columns.append(new_col)
    df.columns = new_columns

    return df

def process_dataframe(df):
    """
    Applies additional processing to a DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to be processed.

    Returns:
        pd.DataFrame: The processed DataFrame.
    """
    # Check for the existence of columns before applying operations
    if 'Age' in df.columns:
        df['Age'] = df['Age'].astype(str).str[:2]
    else:
        df['Age'] = None

    if 'Pos' in df.columns:
        df['Position_2'] = df['Pos'].astype(str).str[3:]
        df['Position'] = df['Pos'].astype(str).str[:2]
    else:
        df['Position_2'] = None
        df['Position'] = None

    if 'Nation' in df.columns:
        df['Nation'] = df['Nation'].astype(str).str.split(' ').str.get(1)
    else:
        df['Nation'] = None

    # Remove columns if they exist
    df = df.drop(columns=['Rk', 'Matches'], errors='ignore')

    # Replace abbreviations with full names
    position_mapping = {'MF': 'Midfielder', 'DF': 'Defender', 'FW': 'Forward', 'GK': 'Goalkeeper'}
    df['Position'] = df['Position'].replace(position_mapping)
    df['Position_2'] = df['Position_2'].replace(position_mapping)

    return df
```

And boring but quick manual part: selecting the URLs from each tab I wanted to gather info from and then turning them into dataframes, so I could merge the data from all tabs and visualize all the metrics.

```
# URLs and table IDs
tables_info = [\
    ('https://fbref.com/en/comps/10/stats/Championship-Stats', 'stats_standard'),\
    ('https://fbref.com/en/comps/10/shooting/Championship-Stats', 'stats_shooting'),\
    ('https://fbref.com/en/comps/10/passing/Championship-Stats', 'stats_passing'),\
    ('https://fbref.com/en/comps/10/passing_types/Championship-Stats', 'stats_passing_types'),\
    ('https://fbref.com/en/comps/10/gca/Championship-Stats', 'stats_gca'),\
    ('https://fbref.com/en/comps/10/defense/Championship-Stats', 'stats_defense'),\
    ('https://fbref.com/en/comps/10/possession/Championship-Stats', 'stats_possession'),\
    ('https://fbref.com/en/comps/10/playingtime/Championship-Stats', 'stats_playing_time'),\
    ('https://fbref.com/en/comps/10/misc/Championship-Stats', 'stats_misc'),\
]

# Dictionary to store the processed DataFrames
dataframes = {}

# Iterate over each URL and table ID
for url, table_id in tables_info:
    # Fetch and clean the table
    df = get_clean_table(url, table_id)
    # Apply the additional processing
    df = process_dataframe(df)
    # Store the DataFrame in the dictionary using the table ID as the key
    dataframes[table_id] = df
```

Resultant dataframe up till this point:

To select the relevant metrics for midfielders and forwards I used a dictionary that included key-value pairs of the lists of variables I needed:

```
columns_to_retain = {
    'stats_standard': ['Player', 'Nation', 'Squad', 'Age', 'Born', 'Playing Time 90s', 'Position_2', 'Position'],
    'stats_passing_types': ['Player', 'Squad', '90s', 'Pass Types TB','Pass Types Sw',\
                            'Pass Types Crs', 'Outcomes Cmp', 'Outcomes Blocks'],
    'stats_passing': ['Player', 'Squad', '90s', 'Total Cmp', 'Total Att',\
       'Total Cmp%', 'Short Cmp', 'Short Att',\
       'Short Cmp%', 'Medium Cmp', 'Medium Att',\
       'Medium Cmp%', 'Long Cmp', 'Long Att',\
       'Long Cmp%', 'Ast', '1/3', 'PPA', 'PrgP'],
    'stats_playing_time': ['Player', 'Squad', 'Playing Time 90s', 'Playing Time MP','Playing Time Min'],
    'stats_shooting': ['Player', 'Squad', '90s', 'Standard Gls', 'Standard Sh', 'Standard SoT', 'Standard SoT%',\
       'Standard Sh/90', 'Standard SoT/90'],
    'stats_gca': ['Player', 'Squad', '90s', 'SCA SCA','GCA GCA'],
    'stats_defense': ['Player', 'Squad', '90s', 'Tackles Tkl',\
       'Tackles TklW', 'Tackles Def 3rd', 'Tackles Mid 3rd', 'Tackles Att 3rd', 'Blocks Blocks', 'Blocks Sh', 'Blocks Pass', 'Int', 'Clr', 'Err'],
    'stats_possession': ['Player', 'Squad', '90s', 'Touches Touches', 'Touches Mid 3rd', 'Touches Att 3rd', 'Touches Att Pen',\
       'Take-Ons Att', 'Take-Ons Succ', 'Take-Ons Succ%', 'Carries Carries', 'Carries PrgC', 'Carries 1/3', 'Carries CPA',\
       'Carries Mis', 'Carries Dis', 'Receiving Rec', 'Receiving PrgR'],
    'stats_misc': ['Player', 'Squad', '90s', 'Performance Off',\
       'Performance Crs', 'Performance Int', 'Performance TklW',\
       'Performance Recov', 'Aerial Duels Won', 'Aerial Duels Lost',\
       'Aerial Duels Won%']
}
```

Final function to obtain the merged dataframe with all the selected variables:

```
def merge_dataframes(dataframes_dict, columns_dict):
    """
    Merges the dataframes from `dataframes_dict` by filtering the required columns from `columns_dict`.

    Args:
        dataframes_dict (dict): Dictionary of processed dataframes.
        columns_dict (dict): Dictionary with the columns to retain for each dataframe.

    Returns:
        pd.DataFrame: Merged DataFrame with the specified columns.
    """
    filtered_dfs = []

    # Filter the columns to retain from each dataframe, only if the columns exist
    for key, df in dataframes_dict.items():
        if key in columns_dict:
            print(f"Columns available in '{key}': {df.columns.tolist()}")  # Debug: print available columns
            columns_to_retain = [col for col in columns_dict[key] if col in df.columns]
            print(f"Columns to retain for '{key}': {columns_to_retain}")  # Debug: print columns to retain
            df_filtered = df[columns_to_retain].copy()
            df_filtered.columns = [f"{col}_{key}" if col not in ['Player', 'Squad'] else col for col in df_filtered.columns]
            filtered_dfs.append(df_filtered)

    # Concatenate all dataframes on 'Player' and 'Squad'
    merged_df = pd.concat(filtered_dfs, axis=1)

    # Remove duplicate columns for 'Player' and 'Squad'
    merged_df = merged_df.loc[:, ~merged_df.columns.duplicated()]

    return merged_df

merged_dataframe = merge_dataframes(dataframes, columns_to_retain)
```

The dataframe still had a lot of NaN values that needed to be cleansed, but the process to obtain data for other leagues (League One and League Two in this case) is good to go.

I need to mention that I used these references as inspiration to drive my own analysis:

[How to scrape and personalize data from FBref with Python: A guide to unlocking Football Insights](https://medium.com/@ricardoandreom/how-to-scrape-and-personalize-data-from-fbref-with-python-a-guide-to-unlocking-football-insights-7e623607afca)

[The Super Easy Way to Scrape FBREF for Free Soccer Data](https://www.youtube.com/watch?v=I0TB9m_hyCo)

There are also other approaches like this one from Henrik who kindly referenced mine:

[Scraping Fbref —Creating a Pipeline](https://medium.com/@henrik.schjoth/scraping-fbref-creating-a-pipeline-f5c9c23ba9da)

So, if you’re into scouting/football analytics and what to try it for yourself, give it a go!

There’s more than one way to get to a solution.

I encourage you to find yours and see how it works.
