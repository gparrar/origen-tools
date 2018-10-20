#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import pprint
import datetime
import argparse
from datetime import datetime, timedelta


# parser = argparse.ArgumentParser()
# parser.add_argument("member")
# args = parser.parse_args()
# print args.echo

# Authentication
def get_token():
    credentials = {"password":"alfi8benito","login":"admin@origencowork"}
    r = requests.post("https://api.e-resto.com/authenticate", data=credentials)
    token = r.json()['token']
    headers = {
    'Authorization':'Bearer %s' % token,
    'accept': 'application/json, text/plain, */*'
    }
    return headers


# Members
def get_list_of_members():
    headers = get_token()
    r = requests.get('https://api.e-resto.com/guests', headers=headers)
    raw_members = r.json()
    members = []
    for k, v in raw_members.iteritems():
        member = {}
        if isinstance(v, dict):
            member['id'] = v['id']
            member['name'] = v['name']
            member['email'] = v['email']
            member['balance'] = v['currentAccountBalance']
            members.append(member)
    return members

# get_list_of_members()
def get_member_id(name):
    members = get_list_of_members()
    member_id = 0
    for member in members:
        if member['name'] == name:
            member_id = member['id']
    return member_id

# Products
def get_products():
    headers = get_token()
    r = requests.get('https://api.e-resto.com/products?a=-1', headers=headers)
    raw_products = r.json()
    products = []
    for k, v in raw_products.iteritems():
        product = {}
        if isinstance(v, dict):
            product['name'] = v['name'].encode('utf-8')
            product['id'] = v['id']
            product['price'] = v['price']
            products.append(product)
    return products



# Sales
def get_period_sales(date_from, date_to, name):
    headers = get_token()
    member_id = get_member_id(name)
    r = requests.get('https://api.e-resto.com/sales?dc=0&g=' + str(member_id) + '&t1=' + date_from + 'T03:00:00.000Z&t2=' + date_to + 'T03:00:00.000Z', headers=headers)
    raw_sales = r.json()
    # pprint.pprint(raw_sales)
    sales = []
    # for k, v in raw_sales.iteritems():
    #     sale = {}
    #     if isinstance(v, dict):
    return raw_sales

def get_today_sales(name):
    headers = get_token()
    member_id = get_member_id(name)
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    r = requests.get('https://api.e-resto.com/sales?dc=0&g=' + str(member_id) + '&t1=' + str(today) + 'T03:00:00.000Z&t2=' + str(tomorrow) + 'T03:00:00.000Z', headers=headers)
    raw_sales = r.json()
    return raw_sales


# Statistics
def get_user_statistics(name, date_from, date_to):
    sales = get_period_sales(date_from, date_to, name)
    # pprint.pprint(sales)
    total = 0
    times = 0
    durations = []
    for k, v in sales.iteritems():
        if isinstance(v, dict):
            if v['discounts']:
                if v['discounts'][0]['canceled'] == True:
                    continue
            if v['payments']:
                total += v['payments'][0]['amount']
            times += 1
            duration = datetime.strptime(v['closedAt'], '%Y-%m-%dT%H:%M:%S-03:00') - datetime.strptime(v['createdAt'], '%Y-%m-%dT%H:%M:%S-03:00')
            durations.append(duration)
    if durations:
        avg_time = sum(durations, timedelta(0)) / len(durations)
        avg_time = avg_time - timedelta(microseconds=avg_time.microseconds)
    else:
        avg_time = 0
    if times != 0:
        avg_ticket = total / times
    else:
        avg_ticket = 0
    stat = (name, times, total, avg_ticket, str(avg_time))
    return stat

stats = []
for user in get_list_of_members():
    stats.append(get_user_statistics(user['name'],'2018-01-01', '2019-01-01'))
print stats

for stat in stats:
    print '%s\t%s\t%s\t%s\t%s' % (stat[0],stat[1],stat[2],stat[3],stat[4])

# Check
def generate_check(name):
    sales = get_period_sales('2018-07-27', '2018-10-16', name)
    products = get_products()
    additions = []
    # pprint.pprint(sales)
    for k, v in sales.iteritems():
        additions.append(v['closedAt'])
        for addition in v['additions']:
            if addition['canceled'] == None:
                if addition['comboAdditions']:
                    combos = addition['comboAdditions']
                    for combo in combos:
                        additions.append(combo['productId'])
                additions.append(addition['productId'])
    check = []

    for product in products:
        if product['id'] in additions:
            check_item = {}
            check_item['name'] = product['name']
            check_item['price'] = product['price']
            check.append(check_item)
    return check

#
# checks = generate_check('Leandro Swietarski')
# for check in checks:
#     pprint.pprint(check)
