import re
import ast
from datetime import timedelta
import csv
from googleapiclient.discovery import build

key = 'your_api_key'

youtube = build('youtube', 'v3', developerKey=key)

request1 = youtube.videos().list(
    part="contentDetails, snippet, statistics, status",
    id="17mKmKQqV1U"
    )
response1 = request1.execute()

request2 = youtube.videoCategories().list(
    part="snippet",
    regionCode="US"
    )
response2 = request2.execute()

def remove_brackets(x):
    """Remove brackets surrounding the items value to turn the data into a dictionary instead of a list. This makes it easier to extract data"""
    nstring = str(x)
    beginning_bracket = re.sub(r"'items': \[{", "'items' : {", nstring)
    ending_bracket = re.sub(r"}], 'pageInfo'", "}, 'pageInfo'", beginning_bracket)
    response_d = ast.literal_eval(ending_bracket)

    return response_d


def cleanup_data(response_d):
    stats = response_d['items']['statistics']

    content_deets_to_modify = response_d['items']['contentDetails']
    content_deets_updated = format_duration(content_deets_to_modify)

    snippet = response_d['items']['snippet']
    del snippet['localized']

    combine_data(stats, content_deets_updated, snippet)

    return video_data_entries


def format_duration(content_deets):
    """Format the duration of the video into a tally of seconds via re"""
    sec_patrn = re.compile(r'(\d+)S')
    min_patrn = re.compile(r'(\d+)M')
    hr_patrn = re.compile(r'(\d+)H')

    for item in content_deets:
        duration = content_deets['duration']

        seconds = sec_patrn.search(duration)
        minutes = min_patrn.search(duration)
        hours = hr_patrn.search(duration)

        seconds = int(seconds.group(1)) if seconds else 0
        minutes = int(minutes.group(1)) if minutes else 0
        hours = int(hours.group(1)) if hours else 0

        vid_seconds = timedelta(
            hours=hours,
            minutes=minutes,
            seconds=seconds
        ).total_seconds()

        content_deets['duration'] = vid_seconds

        return content_deets


video_data_entries = []
def combine_data(stats, content_deets_updated, snippet):
    """For each video this combines the dictionarys with important information then enters the combined group into a list"""
    video_data = dict(stats)
    video_data.update(content_deets_updated)
    video_data.update(snippet)

    x = update_category_info(video_data)

    video_data_entries.append(x)

def export(video_data_entries):
    # columns = list(video_data_entries.keys())
    with open('Names.csv', 'w', newline='') as csvfile:
        columns = ['viewCount', 'likeCount', 'dislikeCount', 'favoriteCount', 'commentCount', 'duration', 'dimension',
                   'definition', 'caption', 'licensedContent', 'contentRating', 'projection', 'publishedAt',
                   'channelId', 'title', 'description', 'thumbnails', 'channelTitle', 'tags', 'categoryId',
                   'liveBroadcastContent']
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        writer.writerows(video_data_entries)


list_of_category_info = response2['items']
def update_category_info(combined_dict):
    category_dict = {}
    for elem in list_of_category_info:
           category_dict[elem['id']] = elem['snippet']['title']

    for item in category_dict:
        if item == combined_dict['categoryId']:
            combined_dict['categoryId'] = category_dict[item]

    return combined_dict


response_d = remove_brackets(response1)

cleanup_data(response_d)

export(video_data_entries)
