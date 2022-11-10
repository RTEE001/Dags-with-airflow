import requests
from airflow.models import Variable
import json 

TOKEN = Variable.get("TOKEN")
USERNAME = Variable.get("USERNAME")


def read_sql(pr):
    sql_query = open(path.join(ROOT_DIRECTORY, sql_path)).read()
    sql_query = sql_query.format(prs_json)
    return sql_query


def read_url(url):
    url_response = requests.get(url, auth=(USERNAME, TOKEN))
    response = url_response.json()
    return response

def get_timestamps(pr_list):
    timestamps = []
    for i in pr_list:
        for key, val in i.items():
            comments = read_url(f"{val}/reviews")
            if len(comments) == 0:
                url = read_url(val)
                if url["updated_at"] != None:
                    timestamps.append({url["html_url"]: url["updated_at"]})
                else:
                    timestamps.append({url["html_url"]: url["created_at"]})
            else:
                for k in comments:
                    timestamps.append({key: k["submitted_at"]})
    return timestamps

def filter_timestamps_by_latest_time(pr_list):
        result_dict = {}
        for item in pr_list:
            key = list(item.keys())[0]
            if key in result_dict:
                if item[key] > result_dict[key][key]:
                    result_dict.update({key: item})
            else:
                result_dict.update({key: item})
        result_list = [v for k, v in result_dict.items()]
        return result_list

def sort_timestamps(pr_list):
    values = []
    sorted_timestamps = []

    for each_dict in pr_list:
        values.append(list(each_dict.values())[0])

    values.sort(reverse=True)

    for each_dict in pr_list:
        insert_index = values.index(list(each_dict.values())[0])
        sorted_timestamps.insert(insert_index, {
            list(each_dict.keys())[0] : values[insert_index]
        })
    return sorted_timestamps

def get_top_five_prs(pr_list):
    urgent_prs = []
    if len(pr_list) >5:
        for i in range(5):
            urgent_prs.append(pr_list[i])
        return urgent_prs     
    return pr_list
