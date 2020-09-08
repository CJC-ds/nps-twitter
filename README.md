# nps-twitter
Net promoter score mined from twitter thread engagement.

## Reason for project
As organizations become increasingly reliant on Social Media platforms for customer engagement; customers have been given a voice to either complain or praise the efforts of these organizations.

Platforms such as **Twitter** have become increasingly rich in data as customers voluntarily voice their opinions and critique the behaviour and decisions that certain organizations decide to make.

Larger organizations with millions of followers will be bombarded with tweets at rates which are humanly impossible to read.
Therefore the full scope of how customers feel about their new announcement and/or decisions cannot be easily understood through human reading alone.

Feedback is important but it is only valuable when it is noticed, internalized and addressed.

## Aim

This project aims to retrieve and analyze tweets made to specific twitter threads, and the overall sentiment for the threads will be analyzed along with the most prevalent words associated with the positive and negative sentiments.

## Use case example

### @FallGuysGame
[**@FallGuysGame**](https://twitter.com/FallGuysGame) is a new videogame with a social media following of 1.4 Million users. Each of their tweets have no less than 1k likes. The number of comments made to each twitter thread ranges from 137 to 3.7k.

Previously, the team at **@FallGuysGame** have made an announcement about removing steam family share feature for their game, in efforts to combat cheaters exploiting the system to avoid bans.
The decision was met with mixed opinions.
People that play **Fall Guys** on steam family share were disappointed and outraged, while those that didn't, praised the team's efforts for combating game cheaters.

### Getting started.
In order to use the code for `get_replies.py`, you are first required to setup a Twitter [developer account](https://developer.twitter.com/en).

Then create a `credentials.ini` file with the format below.
Insert your own api keys.

```
[API]
key=YOUR_API_KEY
secret=YOUR_API_SECRET
[Access]
token=YOUR_ACCESS_TOKEN
secret=YOUR_ACCESS_SECRET
[Bearer]
token=YOUR_BEARER_TOKEN
```
