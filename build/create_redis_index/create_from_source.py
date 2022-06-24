"""Create source json file from beer extracts."""

import json
import pandas as pd

def create_json():
    """Create source json file and deduplicate
    """
    data = []

    def flatten(data):
        flat_data = {}
        for k, v in data.items():
            if isinstance(v, dict):
                for sub_k, sub_v in v.items():
                    new_key = f"{k}.{sub_k}"
                    flat_data[new_key] = sub_v
            else:
                flat_data[k] = v
        return flat_data

    for i in range(0, 13):
        fname = f'../../data/raw_data/get_beers_batch_{i}_1606102731.json'
        with open(fname, 'r') as f:
            temp = json.load(f)
        data += temp

    temp_data = []
    for item in data:
        temp_data.append(flatten(item))
    data = temp_data
    temp_data = []

    df = pd.DataFrame(data)

    df = df.drop_duplicates(subset=['name', 'brewer.name'], keep='first')
    for i in df.columns.values:
        df[i] = df[i].fillna('')
    df['style'] = pd.Categorical(df['style'])
    df['style_code'] = df['style'].cat.codes
    df.reset_index(drop=True, inplace=True)

    final_data = []

    for idx, row in df.iterrows():
        final_data.append({
            "id": row.get('id', ''),
            "name": row.get('name', ''),
            "style": row.get('style', ''),
            "description": row.get('description', ''),
            "abv": row.get('abv', ''),
            "ibu": row.get('ibu', ''),
            "was_modified": row.get('was_modified', 'no'),
            "brewer": {
                "id": row.get('brewer.id', ''),
                "name": row.get('brewer.name', ''),
                "description": row.get('brewer.description', ''),
                "short_description": row.get('brewer.short_description', ''),
                "url": row.get('brewer.url', ''),
                "facebook_url": row.get('brewer.facebook_url', ''),
                "twitter_url": row.get('brewer.twitter_url', ''),
                "instagram_url": row.get('brewer.instagram_url', ''),
            }
        })

    with open('final_data_file.json', 'w') as f:
        json.dump(final_data, f)
    print("Move the final_data_file.json to the production folder")


if __name__ == "__main__":
    create_json()
