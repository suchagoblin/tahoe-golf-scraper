import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class GolfEventScraper:
    def __init__(self):
        self.events = []
        self.courses = {
            'Edgewood Tahoe': {
                'url': 'https://www.edgewood-tahoe.com/golf/tournaments-events',
                'backup_url': 'https://www.edgewood-tahoe.com'
            },
            'Northstar Golf': {
                'url': 'https://www.northstarcalifornia.com/golf/golf-events',
                'backup_url': 'https://www.northstarcalifornia.com/golf'
            },
            'Lake Tahoe Golf Course': {
                'url': 'https://www.laketahoegc.com/events',
                'backup_url': 'https://www.laketahoegc.com'
            },
            'Incline Village Golf': {
                'url': 'https://www.ivgid.org/golf/tournaments-events',
                'backup_url': 'https://www.ivgid.org/golf'
            }
        }
    
    def scrape_course_events(self, course_name, course_info):
        """Scrape events from a golf course website"""
        events_found = []
        
        try:
            print(f"🏌️ Checking {course_name}...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            # Try main URL first, then backup
            urls_to_try = [course_info['url'], course_info['backup_url']]
            
            for url in urls_to_try:
                try:
                    response = requests.get(url, headers=headers, timeout=15)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for event-related content
                    event_keywords = [
                        'tournament', 'camp', 'junior', 'lesson', 'event', 
                        'scramble', 'league', 'clinic', 'championship', 
                        'outing', 'fundraiser', 'member guest'
                    ]
                    
                    # Search in various HTML elements
                    elements_to_search = soup.find_all([
                        'div', 'p', 'h1', 'h2', 'h3', 'h4', 'li', 
                        'span', 'td', 'article', 'section'
                    ])
                    
                    for element in elements_to_search:
                        text = element.get_text().strip()
                        
                        # Skip if too short or too long
                        if len(text) < 30 or len(text) > 300:
                            continue
                        
                        # Check if contains event keywords
                        text_lower = text.lower()
                        if any(keyword in text_lower for keyword in event_keywords):
                            # Look for dates in the text
                            date_patterns = [
                                r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}',
                                r'\d{1,2}/\d{1,2}/\d{2,4}',
                                r'\d{1,2}-\d{1,2}-\d{2,4}'
                            ]
                            
                            has_date = any(__import__('re').search(pattern, text_lower) for pattern in date_patterns)
                            
                            if has_date or any(urgent_keyword in text_lower for urgent_keyword in ['register', 'sign up', 'deadline']):
                                events_found.append({
                                    'text': text.strip()[:250] + ('...' if len(text) > 250 else ''),
                                    'relevance': 'high' if has_date else 'medium'
                                })
                    
                    break  # If successful, don't try backup URL
                    
                except requests.exceptions.RequestException as e:
                    print(f"Failed to load {url}: {e}")
                    continue
            
            # Remove duplicates and sort by relevance
            unique_events = []
            seen_texts = set()
            
            for event in events_found:
                if event['text'] not in seen_texts:
                    seen_texts.add(event['text'])
                    unique_events.append(event)
            
            # Sort by relevance (high first) and limit to top 5
            unique_events.sort(key=lambda x: x['relevance'] == 'high', reverse=True)
            unique_events = unique_events[:5]
            
            if unique_events:
                self.events.append({
                    'course': course_name,
                    'url': course_info['url'],
                    'events': [event['text'] for event in unique_events],
                    'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M UTC')
                })
                print(f"✅ Found {len(unique_events)} events at {course_name}")
            else:
                print(f"❌ No events found at {course_name}")
                
        except Exception as e:
            print(f"❌ Error scraping {course_name}: {e}")
    
    def scrape_all_courses(self):
        """Scrape all golf courses for events"""
        print("🏌️ Lake Tahoe Golf Course Event Scraper")
        print("=" * 50)
        
        for course_name, course_info in self.courses.items():
            self.scrape_course_events(course_name, course_info)
        
        print("=" * 50)
        print(f"✅ Scraping complete! Found events at {len(self.events)} courses.")
        return self.events
    
    def format_for_wix_post(self):
        """Format events for Wix community post"""
        if not self.events:
            return None
        
        post_content = f"""🏌️ **New Golf Events - Lake Tahoe Area**
*Updated: {datetime.now().strftime('%B %d, %Y')}*

Great opportunities to showcase Slicer Golf Clubs! 🏌️‍♂️

"""
        
        for course_data in self.events:
            post_content += f"**📍 {course_data['course']}**\n"
            
            for i, event in enumerate(course_data['events'], 1):
                # Clean up the event text
                clean_event = event.replace('\n', ' ').replace('\r', '').strip()
                post_content += f"{i}. {clean_event}\n"
            
            post_content += f"🌐 [Visit Website]({course_data['url']})\n\n"
        
        post_content += """---
💡 **Planning to participate?** Let us know which events interest you!
🏌️ These are perfect opportunities to try out Slicer Golf Clubs.

*This update was automatically generated to keep our community informed of local golf opportunities.*"""
        
        return post_content
    
    def send_email_summary(self):
        """Send email summary using GitHub secrets"""
        try:
            # Get email settings from environment variables (GitHub secrets)
            to_email = os.environ.get('TO_EMAIL')
            from_email = os.environ.get('FROM_EMAIL')
            app_password = os.environ.get('EMAIL_APP_PASSWORD')
            
            if not all([to_email, from_email, app_password]):
                print("❌ Email credentials not configured. Skipping email.")
                return False
            
            wix_content = self.format_for_wix_post()
            
            if not wix_content:
                print("📧 No events found - no email sent.")
                return True
            
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = f"🏌️ Lake Tahoe Golf Events - {datetime.now().strftime('%B %d, %Y')}"
            
            email_body = f"""Hi!

Your automated golf course scraper found new events in the Lake Tahoe area.

Here's the content formatted for your Wix community post:

{wix_content}

---

NEXT STEPS:
1. Review the events above
2. Copy the formatted content to your Wix Members Area community discussion
3. Visit course websites to verify details if needed
4. Consider reaching out to courses about Slicer Golf Club partnerships

The scraper will run again tomorrow to check for updates!

Best regards,
Your Automated Golf Event Monitor
"""
            
            msg.attach(MIMEText(email_body, 'plain'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(from_email, app_password)
            server.sendmail(from_email, to_email, msg.as_string())
            server.quit()
            
            print("✅ Email summary sent successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False
    
    def save_results(self):
        """Save results to JSON file for GitHub Actions artifacts"""
        results = {
            'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
            'total_courses_checked': len(self.courses),
            'courses_with_events': len(self.events),
            'events': self.events,
            'wix_post_content': self.format_for_wix_post()
        }
        
        with open('golf_events_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print("💾 Results saved to golf_events_results.json")

def main():
    scraper = GolfEventScraper()
    
    # Scrape all courses
    events = scraper.scrape_all_courses()
    
    # Save results
    scraper.save_results()
    
    # Send email summary
    scraper.send_email_summary()
    
    # Print summary
    print(f"\n📊 SUMMARY:")
    print(f"Courses checked: {len(scraper.courses)}")
    print(f"Events found at: {len(events)} courses")
    
    if events:
        print(f"\n🎯 Ready-to-post content generated!")
        print(f"Check your email for the formatted Wix community post.")

if __name__ == "__main__":
    main()
