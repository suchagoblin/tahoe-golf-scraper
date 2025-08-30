import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
import time
import re

class FixedGolfEventScraper:
    def __init__(self):
        self.events = []
        self.errors = []
        self.courses = {
            'Edgewood Tahoe': {
                'urls': [
                    'https://www.edgewood-tahoe.com',
                    'https://www.edgewood-tahoe.com/golf'
                ],
                'location': 'South Lake Tahoe',
                'phone': '(775) 588-3566'
            },
            'Tahoe Donner Golf Course': {
                'urls': [
                    'https://www.tahoedonner.com/amenities/amenities/golf',
                    'https://www.tahoedonner.com/amenities/amenities/golf/lessons-clinics',
                    'https://www.tahoedonner.com'
                ],
                'location': 'Truckee',
                'phone': '(530) 587-9440'
            },
            'Lake Tahoe Golf Course': {
                'urls': [
                    'https://www.laketahoegc.com',
                    'https://www.laketahoegc.com/golf'
                ],
