import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import time

class ExpandedGolfEventScraper:
    def __init__(self):
        self.events = []
        self.courses = {
            # Lake Tahoe Core Courses
            'Edgewood Tahoe': {
                'url': 'https://www.edgewood-tahoe.com',
                'location': 'South Lake Tahoe',
                'phone': '(775) 588-3566'
            },
            'Lake Tahoe Golf Course': {
                'url': 'https://www.laketahoegc.com',
                'location': 'South Lake Tahoe',
                'phone': '(530) 577-0788'
            },
            'Incline Village Golf': {
                'url': 'https://www.ivgid.org',
                'location': 'Incline Village',
                'phone': '(775) 832-1146'
            },
            
            # Northstar Area
            'Northstar Golf Course': {
                'url': 'https://www.northstarcalifornia.com',
                'location': 'Truckee',
                'phone': '(530) 562-2490'
            },
            'Coyote Moon Golf Course': {
                'url': 'https://www.coyotemoon.com',
                'location': 'Truckee',
                'phone': '(530) 587-0886'
            },
            'Tahoe Donner Golf Course': {
                'url': 'https://www.tahoedonner.com',
                'location': 'Truckee',
                'phone': '(530) 587-9440'
            },
            
            # Reno Area (within 45 minutes)
            'Montreux Golf & Country Club': {
                'url': 'https://www.montreuxgolf.com',
                'location': 'Reno',
                'phone': '(775) 849-9444'
            },
            'Arrowcreek Country Club': {
                'url': 'https://www.arrowcreek.com',
                'location': 'Reno',
                'phone': '(775) 850-4471'
            },
            'Red Hawk Golf Course': {
                'url': 'https://www.redhawkgolf.com',
                'location': 'Sparks',
                'phone': '(775) 626-6000'
            },
            'Wildcreek Golf Course': {
                'url': 'https://www.wildcreekgolf.com',
                'location': 'Sparks',
                'phone': '(775) 673-3100'
            },
            
            # South Lake Tahoe Area
            'Bijou Municipal Golf Course': {
                'url': 'https://www.cityofslt.us',
                'location': 'South Lake Tahoe',
                'phone': '(530) 542-6097'
            },
            'Tahoe Paradise Golf Course': {
                'url': 'https://www.tahoeparadisegolf.com',
                'location': 'South Lake Tahoe',
                'phone': '(530) 577-2121'
            },
            
            # Carson Valley (30 minutes south)
            'Genoa Lakes Golf Club': {
                'url': 'https://www.genoalakes.com',
                'location': 'Genoa',
                'phone': '(775) 782-4653'
            },
            'Carson Valley Golf Course': {
                'url': 'https://www.carsonvalleygolf.com',
                'location': 'Gardnerville',
                'phone': '(775) 265-3181'
            }
        }
    
    def get_expanded_event_keywords(self):
        """Comprehensive list of golf event keywords"""
        return [
            # Tournaments
            'tournament', 'championship', 'scramble', 'best ball', 'member guest',
            'club championship', 'stroke play', 'match play', 'shotgun start',
            'tee time', 'qualifying', 'playoff', 'bracket',
            
            # Lessons & Instruction
            'lesson', 'instruction', 'clinic', 'golf school', 'academy',
            'teaching pro', 'pga pro', 'swing', 'putting', 'chipping',
            'driving range', 'practice', 'golf tips',
            
            # Junior Programs
            'junior', 'kids', 'youth', 'camp', 'children', 'beginner',
            'junior golf', 'golf camp', 'summer camp', 'after school',
            'pga junior', 'first tee', 'youth program',
            
            # Leagues & Regular Events
            'league', 'weekly', 'men league', 'women league', 'couples league',
            'senior league', 'twilight league', 'nine hole league',
            
            # Special Events
            'outing', 'fundraiser', 'charity', 'benefit', 'corporate',
            'group event', 'private event', 'banquet', 'dinner',
            'awards', 'prizes', 'golf package',
            
            # Seasonal/Holiday
            'spring', 'summer', 'fall', 'winter', 'holiday', 'memorial day',
            'july 4th', 'labor day', 'thanksgiving', 'christmas',
            
            # Registration/Booking
            'register', 'sign up', 'book', 'reservation', 'deadline',
            'entry fee', 'cost', 'price', 'payment', 'deposit'
        ]
    
    def scrape_course_events(self, course_name, course_info):
        """Enhanced event scraping with better detection"""
        events_found = []
        
        try:
            print(f"🏌️ Checking {course_name} ({course_info['location']})...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.google.com/',
            }
            
            # Try multiple URL variations
            urls_to_try = [
                course_info['url'],
                course_info['url'] + '/events',
                course_info['url'] + '/tournaments',
                course_info['url'] + '/golf',
                course_info['url'] + '/golf/events',
                course_info['url'] + '/programs',
                course_info['url'] + '/calendar'
            ]
            
            event_keywords = self.get_expanded_event_keywords()
            
            for url in urls_to_try:
                try:
                    print(f"  Trying: {url}")
                    response = requests.get(url, headers=headers, timeout=20)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Remove common navigation/footer elements
                        for element in soup(['nav', 'footer', 'header', 'script', 'style']):
                            element.decompose()
                        
                        # Get all text content
                        page_text = soup.get_text()
                        
                        # Split into paragraphs/sections
                        sections = re.split(r'\n\s*\n', page_text)
                        
                        for section in sections:
                            section = section.strip()
                            section_lower = section.lower()
                            
                            # Skip if too short or too long
                            if len(section) < 20 or len(section) > 500:
                                continue
                            
                            # Check for event keywords
                            keyword_matches = [kw for kw in event_keywords if kw in section_lower]
                            
                            if keyword_matches:
                                # Look for dates, times, prices
                                has_date = bool(re.search(r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}', section_lower))
                                has_time = bool(re.search(r'\d{1,2}:\d{2}|am|pm', section_lower))
                                has_price = bool(re.search(r'\$\d+|fee|cost|price', section_lower))
                                has_contact = bool(re.search(r'call|phone|contact|register|sign.?up', section_lower))
                                
                                # Score the relevance
                                relevance_score = len(keyword_matches)
                                if has_date: relevance_score += 2
                                if has_time: relevance_score += 1
                                if has_price: relevance_score += 1
                                if has_contact: relevance_score += 1
                                
                                if relevance_score >= 2:  # At least one keyword + one other indicator
                                    events_found.append({
                                        'text': section[:300] + ('...' if len(section) > 300 else ''),
                                        'keywords': keyword_matches[:3],  # Top 3 matching keywords
                                        'score': relevance_score,
                                        'source_url': url
                                    })
                    
                    # If we found events, don't need to try more URLs
                    if events_found:
                        print(f"  ✅ Found {len(events_found)} potential events")
                        break
                    
                    time.sleep(1)  # Be respectful between requests
                    
                except requests.exceptions.RequestException as e:
                    print(f"  ❌ Failed to load {url}: {str(e)[:50]}...")
                    continue
            
            # Process and rank events
            if events_found:
                # Remove duplicates and sort by relevance score
                unique_events = {}
                for event in events_found:
                    # Use first 100 characters as key to avoid exact duplicates
                    key = event['text'][:100]
                    if key not in unique_events or unique_events[key]['score'] < event['score']:
                        unique_events[key] = event
                
                # Sort by score and take top 5
                sorted_events = sorted(unique_events.values(), key=lambda x: x['score'], reverse=True)[:5]
                
                self.events.append({
                    'course': course_name,
                    'location': course_info['location'],
                    'phone': course_info['phone'],
                    'url': course_info['url'],
                    'events': sorted_events,
                    'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M UTC')
                })
                
                print(f"  📋 Saved top {len(sorted_events)} events for {course_name}")
            else:
                print(f"  ❌ No events found at {course_name}")
                
        except Exception as e:
            print(f"❌ Error scraping {course_name}: {e}")
        
        # Respectful delay between courses
        time.sleep(2)
    
    def scrape_all_courses(self):
        """Scrape all golf courses for events"""
        print("🏌️ EXPANDED LAKE TAHOE AREA GOLF EVENT SCRAPER")
        print("=" * 60)
        print(f"Checking {len(self.courses)} courses in the Lake Tahoe region...")
        print("=" * 60)
        
        for course_name, course_info in self.courses.items():
            self.scrape_course_events(course_name, course_info)
        
        print("=" * 60)
        print(f"✅ Scraping complete!")
        print(f"📊 Total courses checked: {len(self.courses)}")
        print(f"📋 Courses with events: {len(self.events)}")
        
        if self.events:
            total_events = sum(len(course['events']) for course in self.events)
            print(f"🎯 Total events found: {total_events}")
        
        return self.events
    
    def format_for_wix_post(self):
        """Format events for Wix community post"""
        if not self.events:
            return None
        
        post_content = f"""🏌️ **Golf Events & Opportunities - Lake Tahoe Region**
*Updated: {datetime.now().strftime('%B %d, %Y')} | {len(self.events)} courses with events*

Great opportunities to showcase Slicer Golf Clubs throughout the region! 🏌️‍♂️

"""
        
        # Group by location
        locations = {}
        for course_data in self.events:
            location = course_data['location']
            if location not in locations:
                locations[location] = []
            locations[location].append(course_data)
        
        for location, courses in locations.items():
            post_content += f"## 📍 {location} Area\n\n"
            
            for course_data in courses:
                post_content += f"**{course_data['course']}**\n"
                post_content += f"📞 {course_data['phone']}\n"
                
                for i, event in enumerate(course_data['events'], 1):
                    # Show keywords that matched
                    keywords = ', '.join(event['keywords'])
                    post_content += f"{i}. {event['text'][:200]}{'...' if len(event['text']) > 200 else ''}\n"
                    post_content += f"   *Keywords: {keywords}*\n"
                
                post_content += f"🌐 [Visit Website]({course_data['url']})\n\n"
        
        post_content += """---
💡 **See something interesting?** Let us know which events you're considering!
🏌️ These are perfect opportunities to try Slicer Golf Clubs at various skill levels.
📞 **Pro Tip:** Call ahead to confirm event details and ask about equipment demos.

*This update covers {total_courses} courses within 45 minutes of Lake Tahoe. Updated automatically to keep our community informed of regional golf opportunities.*""".format(total_courses=len(self.courses))
        
        return post_content
    
    def save_detailed_results(self):
        """Save comprehensive results"""
        results = {
            'scrape_info': {
                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
                'total_courses_checked': len(self.courses),
                'courses_with_events': len(self.events),
                'search_radius': 'Lake Tahoe region (45 minute drive)',
                'keywords_used': len(self.get_expanded_event_keywords())
            },
            'course_summary': [
                {
                    'name': course,
                    'location': info['location'],
                    'phone': info['phone'],
                    'events_found': len([e for e in self.events if e['course'] == course])
                }
                for course, info in self.courses.items()
            ],
            'events': self.events,
            'wix_post_content': self.format_for_wix_post()
        }
        
        with open('detailed_golf_events.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print("💾 Detailed results saved to detailed_golf_events.json")
        
        # Also save a simple summary
        summary = f"""GOLF EVENT SCRAPER SUMMARY
Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p UTC')}

COVERAGE:
• {len(self.courses)} courses checked across Lake Tahoe region
• {len(self.events)} courses found with events
• Search radius: 45-minute drive from Lake Tahoe

COURSES WITH EVENTS:
"""
        for course_data in self.events:
            summary += f"• {course_data['course']} ({course_data['location']}) - {len(course_data['events'])} events\n"
        
        if not self.events:
            summary += "• No events found this scan\n"
        
        with open('golf_events_summary.txt', 'w') as f:
            f.write(summary)
        
        print("📄 Summary saved to golf_events_summary.txt")

def main():
    scraper = ExpandedGolfEventScraper()
    
    # Scrape all courses
    events = scraper.scrape_all_courses()
    
    # Save detailed results
    scraper.save_detailed_results()
    
    # Print final summary
    print(f"\n🎯 FINAL RESULTS:")
    print(f"Courses in database: {len(scraper.courses)}")
    print(f"Courses with events: {len(events)}")
    
    if events:
        total_events = sum(len(course['events']) for course in events)
        print(f"Total events found: {total_events}")
        print(f"\n📧 Check detailed_golf_events.json for full results!")
        print(f"📋 Ready-to-post content generated for Wix community.")
    else:
        print(f"🔍 No events found. This could mean:")
        print(f"   • Courses don't have current events posted")
        print(f"   • Events are in calendars/booking systems we can't access")
        print(f"   • Need to adjust our search criteria")

if __name__ == "__main__":
    main()
