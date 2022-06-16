# NICEHASH MONITOR
Tracks your nicehash rig's statistics, current hashrate, unpaid balance & 24Hr profitability.


[![Python](https://img.shields.io/badge/python-3.10-blue)](https://www.python.org/downloads/)


## API Reference

#### Get all the stats of the provided rig

```http
  GET /main/api/v2/mining/rig2/{rigId}
```

| Parameter | Type     | Description                                    |
| :-------- | :------- | :-------------------------                     |
| `org_id`  | `string` | **Required**. Your organisation id             |
| `key`     | `string` | **Required**. Your key                         |
| `secret`  | `string` | **Required**. Your account's unique secret code|
| `rigid`   | `string` | **Required**. Your rig-id of which you want to see the stats                         |

### Data received in JSON format.

Nicehash sends the statistics of your rig in the JSON format which contains vital details of your rig.



## Dependencies

Since windows defender is flagging the executable file as a false positive virus, currently you have to download and run the script manually. Here are the list of things you need to install inorder to run this script:

#### • Python:
```http
https://www.python.org/downloads/
```
#### • Tkinter: For the GUI

```http
pip install Tkinter
```
#### • configparser: To create and read the config file
```http
pip install configparser
```
#### • requests: API call
```http
pip install requests
```
#### • beautifulsoup4: Minor webscraping for btc prices
```http
pip install beautifulsoup4
```

