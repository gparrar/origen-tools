#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import pprint
import datetime
import argparse
import slack_service


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


# Inventory
def get_products():
    headers = get_token()
    r = requests.get('https://api.e-resto.com/products?a=-1', headers=headers)
    raw_products = r.json()
    products = []
    for k, v in raw_products.iteritems():
        if isinstance(v, dict):
            if v['stockControl'] is True and v['active'] is True:
                if v['stock'] == None:
                    v['stock'] = 0
                inventory_item = (v['name'].encode('utf-8'), v['stock'], v['productCategoryId'])
                products.append(inventory_item)
    return products

def get_categories():
    headers = get_token()
    r = requests.get('https://api.e-resto.com/product_categories', headers=headers)
    raw_cats = r.json()
    categories = []
    for k, v in raw_cats.iteritems():
        if isinstance(v, dict):
            category = (v['name'].encode('utf-8'), v['id'],)
            categories.append(category)
    return categories

def build_inventory():
    products = get_products()
    categories = get_categories()
    inventory = []
    for category in categories:
        inventory_category = {}
        inventory_category['name'] = category[0]
        inventory_category['products'] = []
        for product in products:
            if product[2] == category[1]:
                inventory_category['products'].append((product[0],int(product[1])))
        inventory.append(inventory_category)
    return inventory

# Messaging
def prepare_message():
    inventory = build_inventory()
    message = "Anoche me metí en el almacen y conté los siguientes productos:\n"
    for item in inventory:
        if not item['products']:
            continue
        message += "*%s* \n" % (item['name'])
        for product in item['products']:
            message += " - _%s:_ *%s* \n" % (product[0],product[1])
    return message

def main():
    slack_channel = "#stock"
    slack_message = prepare_message()
    slack_service.send_slack_message(slack_message, slack_channel)

main()
