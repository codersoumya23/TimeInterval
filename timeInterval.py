
import pandas as pd
import re
from flask import Flask, request, jsonify

app = Flask(__name__)


# Your existing JSON processing function
def process_json(data):
    all_list = []
    for inputs_set in data['inputs']:
        List = []
        n = inputs_set[0]
        names = re.split('\s', inputs_set[1])

        for i in range(2, len(inputs_set)):
            List.append(inputs_set[i])

        xy_split = [tuple(map(int, value.split())) for value in List]

        data = [{"name": name, "x": x, "y": y} for name, (x, y) in zip(names, xy_split)]

        df = pd.DataFrame(data)

        df['abs_diff'] = abs(df['x'] - df['y'])
        merged_list = list(set(df['x'].tolist() + df['y'].tolist()))

        sorted_unique_elements = sorted(merged_list)
        df_result = pd.DataFrame(sorted_unique_elements, columns=['x1'])

        df_result['y1'] = df_result['x1'].shift(-1)

        df_result = df_result[:-1]
        df_result = df_result.astype(int)
        df_result['Names'] = [[] for _ in range(len(inputs_set) - 2)]

        for i in range(len(df)):
            row = df.iloc[i]
            for j in range(len(df_result)):
                row1 = df_result.iloc[j]

                if row1['x1'] >= row['x'] and row['y'] >= row1['y1'] and row['abs_diff'] >= 0:
                    # print(row['name'])
                    df_result.at[j, 'Names'].append(row['name'])
                    # print(df_result)
                    row['abs_diff'] -= 1
                    # print(row['abs_diff'])
        df_result.insert(df_result.columns.get_loc("Names"), "NumStrings", df_result["Names"].apply(len))
        df_result['Names'] = df_result['Names'].apply(sorted)
        formatted_data = df_result.apply(
            lambda row: f"{row['x1']} {row['y1']} {row['NumStrings']} {' '.join(row['Names'])}", axis=1)

        list_of_strings = formatted_data.tolist()

        list_of_strings.insert(0, n)
        # print(df_result)
        all_list.append(list_of_strings)

    return all_list


# Expose a POST endpoint /time-intervals
@app.route('/time-intervals', methods=['POST'])
def time_intervals_post():
    if request.method == 'POST':
        try:
            json_data = request.get_json()
            result = process_json(json_data)
            return jsonify({"answer": result})
        except Exception as e:
            return jsonify({"error": str(e)}), 400


# Expose a GET endpoint /time-intervals
@app.route('/time-intervals', methods=['GET'])
def time_intervals_get():
    try:
        json_data = request.args.get('json_data')
        result = process_json(json_data)
        return jsonify(result)
        #return jsonify({"answer": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4094, debug=True)
