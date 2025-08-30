import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
import time
import re

class SmartGolfEventExtractor:
    def __init__(self):
        self.events = []
        self.errors = []
        self.courses = {
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
            'Tahoe Paradise Golf Course': {
                'url': 'https://www.tahoeparadisegolf.com',
                'location': 'South Lake Tahoe',
                'phone': '(530) 577-2121'
            },
            'Incline Village Golf': {
                'url': 'https://www.ivgid.org',
                'location': 'Incline Village',
                'phone': '(775) 832-1146'
            },
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
            }
        }
        
        # Enhanced keywords for better detection
        self.event_keywords = [
            'tournament', 'scramble', 'camp', 'junior', 'lesson', 
            'league', 'clinic', 'instruction', 'championship',
            'outing', 'register', 'sign up', 'golf school', 'pga'
        ]
    
    def extract_event_details(self, text_section, keywords_found):
        """Extract specific event details from text sections"""
        event_details = {
            'raw_text': text_section,
            'keywords': keywords_found,
            'dates': [],
            'times': [],
            'prices': [],
            'ages': [],
            'contact_info': [],
            'registration_info': []
        }
        
        # Extract dates
        date_patterns = [
            r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(?:st|nd|rd|th)?\s*(?:,\s*)?(?:\d{4}|\d{2})?',
            r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',
            r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{1,2}',
            r'\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)s?',
            r'(?:spring|summer|fall|winter)\s+\d{4}',
            r'\d{4}\s+season'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text_section, re.IGNORECASE)
            event_details['dates'].extend(matches)
        
        # Extract times
        time_patterns = [
            r'\d{1,2}:\d{2}\s*(?:am|pm)',
            r'\d{1,2}\s*(?:am|pm)',
            r'\b(?:morning|afternoon|evening)\b'
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, text_section, re.IGNORECASE)
            event_details['times'].extend(matches)
        
        # Extract prices/costs
        price_patterns = [
            r'\$\d+(?:\.\d{2})?(?:\s*per\s*\w+)?',
            r'(?:cost|fee|price)[:s]?\s*\$?\d+',
            r'\d+\s*dollars?',
            r'free\s+(?:event|program|lesson|clinic)',
            r'no\s+(?:cost|charge|fee)'
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, text_section, re.IGNORECASE)
            event_details['prices'].extend(matches)
        
        # Extract age information
        age_patterns = [
            r'ages?\s+\d+(?:\s*[-to]+\s*\d+)?',
            r'\d+(?:\s*[-to]+\s*\d+)?\s+years?\s+old',
            r'(?:junior|adult|senior|youth|kids?|children)',
            r'(?:beginner|intermediate|advanced)'
        ]
        
        for pattern in age_patterns:
            matches = re.findall(pattern, text_section, re.IGNORECASE)
            event_details['ages'].extend(matches)
        
        # Extract contact information
        contact_patterns = [
            r'\(\d{3}\)\s*\d{3}[-.\s]*\d{4}',
            r'\d{3}[-.\s]*\d{3}[-.\s]*\d{4}',
            r'[\w.-]+@[\w.-]+\.\w+',
            r'(?:call|contact|email|phone)[:s]?\s*[\(\d\w@.-]+',
            r'pro\s*shop',
            r'register(?:ation)?'
        ]
        
        for pattern in contact_patterns:
            matches = re.findall(pattern, text_section, re.IGNORECASE)
            event_details['contact_info'].extend(matches)
        
        # Extract registration information
        registration_patterns = [
            r'register(?:ation)?\s+(?:opens?|begins?|starts?).*',
            r'(?:deadline|due|closes?|ends?).*',
            r'sign\s*up.*',
            r'enrollment.*',
            r'spots?\s+available',
            r'limited\s+(?:space|spots)'
        ]
        
        for pattern in registration_patterns:
            matches = re.findall(pattern, text_section, re.IGNORECASE)
            event_details['registration_info'].extend(matches)
        
        return event_details
    
    def find_event_sections(self, soup):
        """Find sections of the webpage that contain event information"""
        event_sections = []
        
        # Look for common event containers
        event_containers = soup.find_all([
            'div', 'section', 'article', 'li', 'td', 'p'
        ], class_=re.compile(r'event|program|camp|tournament|lesson|clinic', re.I))
        
        # Also look for headers followed by content
        headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        for header in headers:
            header_text = header.get_text().lower()
            if any(keyword in header_text for keyword in self.event_keywords):
                # Get the content following this header
                content = []
                next_element = header.next_sibling
                
                while next_element and len(content) < 5:  # Limit to avoid too much content
                    if hasattr(next_element, 'get_text'):
                        text = next_element.get_text().strip()
                        if text and len(text) > 20:
                            content.append(text)
                    next_element = next_element.next_sibling
                
                if content:
                    event_sections.append({
                        'header': header.get_text().strip(),
                        'content': ' '.join(content)
                    })
        
        # Add any found event containers
        for container in event_containers:
            text = container.get_text().strip()
            if len(text) > 50 and any(keyword in text.lower() for keyword in self.event_keywords):
                event_sections.append({
                    'header': 'Event Container',
                    'content': text
                })
        
        return event_sections
    
    def scrape_course_intelligently(self, course_name, course_info):
        """Intelligently scrape for actual event content"""
        try:
            print(f"🏌️ Intelligently scanning {course_name}...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            # Try multiple golf-specific URLs
            urls_to_try = [
                course_info['url'],
                course_info['url'] + '/golf',
                course_info['url'] + '/programs',
                course_info['url'] + '/lessons',
                course_info['url'] + '/events',
                course_info['url'] + '/tournaments',
                course_info['url'] + '/junior-golf',
                course_info['url'] + '/camps'
            ]
            
            all_events = []
            
            for url in urls_to_try[:4]:  # Limit to 4 URLs to prevent timeout
                try:
                    print(f"  Checking: {url}")
                    response = requests.get(url, headers=headers, timeout=12)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Remove navigation and footer noise
                        for noise in soup(['nav', 'footer', 'header', 'script', 'style']):
                            noise.decompose()
                        
                        # Find event-specific sections
                        event_sections = self.find_event_sections(soup)
                        
                        for section in event_sections:
                            # Check if section contains our keywords
                            section_text = (section['header'] + ' ' + section['content']).lower()
                            found_keywords = [kw for kw in self.event_keywords if kw in section_text]
                            
                            if found_keywords:
                                print(f"    Found event section: {section['header'][:50]}...")
                                
                                # Extract detailed information
                                event_details = self.extract_event_details(
                                    section['header'] + '\n' + section['content'], 
                                    found_keywords
                                )
                                
                                all_events.append({
                                    'title': section['header'],
                                    'source_url': url,
                                    'details': event_details,
                                    'relevance_score': len(found_keywords) + 
                                                     len(event_details['dates']) + 
                                                     len(event_details['prices']) + 
                                                     len(event_details['contact_info'])
                                })
                        
                        if all_events:
                            break  # Found events, don't need to check more URLs
                    
                    time.sleep(1)  # Be respectful
                    
                except requests.exceptions.RequestException as e:
                    print(f"    Error loading {url}: {str(e)[:30]}...")
                    continue
            
            if all_events:
                # Sort by relevance score and take the best ones
                all_events.sort(key=lambda x: x['relevance_score'], reverse=True)
                top_events = all_events[:3]  # Top 3 most relevant events
                
                self.events.append({
                    'course': course_name,
                    'location': course_info['location'],
                    'phone': course_info['phone'],
                    'url': course_info['url'],
                    'events_found': len(all_events),
                    'top_events': top_events,
                    'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M UTC'),
                    'status': 'success'
                })
                
                print(f"  ✅ Extracted {len(all_events)} detailed events")
            else:
                print(f"  ❌ No detailed events found")
                self.record_error(course_name, "No events found")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:50]}")
            self.record_error(course_name, str(e)[:50])
        
        time.sleep(2)  # Respectful delay
    
    def record_error(self, course_name, error_msg):
        """Record errors for debugging"""
        self.errors.append({
            'course': course_name,
            'error': error_msg,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M UTC')
        })
    
    def scrape_all_courses(self):
        """Scrape all courses intelligently"""
        print("🏌️ SMART GOLF EVENT EXTRACTOR - LAKE TAHOE")
        print("=" * 50)
        print(f"Intelligently extracting event details from {len(self.courses)} courses...")
        print("=" * 50)
        
        for i, (course_name, course_info) in enumerate(self.courses.items(), 1):
            print(f"\n[{i}/{len(self.courses)}] {course_name}...")
            self.scrape_course_intelligently(course_name, course_info)
        
        print("\n" + "=" * 50)
        print("✅ Smart extraction complete!")
        return self.events
    
    def format_for_wix_community(self):
        """Format extracted events for Wix community post"""
        if not self.events:
            return "No detailed golf events found in this scan."
        
        post_content = f"""🏌️ **Detailed Golf Events & Programs - Lake Tahoe Area**
*Updated: {datetime.now().strftime('%B %d, %Y')} | {len(self.events)} courses with detailed events*

Perfect opportunities for Slicer Golf Club enthusiasts! 🏌️‍♂️

"""
        
        for course_data in self.events:
            post_content += f"## 📍 **{course_data['course']}** ({course_data['location']})\n"
            post_content += f"📞 {course_data['phone']} | 🌐 {course_data['url']}\n\n"
            
            for i, event in enumerate(course_data['top_events'], 1):
                post_content += f"### {i}. {event['title']}\n"
                
                details = event['details']
                
                # Add dates if found
                if details['dates']:
                    unique_dates = list(set(details['dates']))[:3]
                    post_content += f"📅 **Dates:** {', '.join(unique_dates)}\n"
                
                # Add times if found
                if details['times']:
                    unique_times = list(set(details['times']))[:3]
                    post_content += f"🕐 **Times:** {', '.join(unique_times)}\n"
                
                # Add prices if found
                if details['prices']:
                    unique_prices = list(set(details['prices']))[:3]
                    post_content += f"💰 **Cost:** {', '.join(unique_prices)}\n"
                
                # Add age info if found
                if details['ages']:
                    unique_ages = list(set(details['ages']))[:3]
                    post_content += f"👥 **Ages/Level:** {', '.join(unique_ages)}\n"
                
                # Add contact info if found
                if details['contact_info']:
                    clean_contacts = [c for c in details['contact_info'] if len(c) > 3][:2]
                    if clean_contacts:
                        post_content += f"📞 **Contact:** {', '.join(clean_contacts)}\n"
                
                post_content += f"\n"
            
            post_content += "---\n\n"
        
        post_content += f"""
💡 **These are real, actionable opportunities!** Contact the courses directly to:
- Ask about equipment demos with Slicer Golf Clubs
- Inquire about group discounts for our community
- Sign up for programs that match your skill level

📧 **Found this helpful?** Let us know which programs you're interested in!

*Automatically extracted {sum(c['events_found'] for c in self.events)} total events across the region.*
"""
        
        return post_content
    
    def save_intelligent_results(self):
        """Save detailed extraction results"""
        results = {
            'extraction_summary': {
                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M UTC'),
                'courses_checked': len(self.courses),
                'courses_with_detailed_events': len(self.events),
                'total_events_extracted': sum(c['events_found'] for c in self.events),
                'extraction_method': 'intelligent_content_analysis'
            },
            'detailed_events': self.events,
            'errors': self.errors,
            'wix_community_post': self.format_for_wix_community()
        }
        
        # Always save the required file
        with open('golf_events_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print("✅ Intelligent results saved to golf_events_results.json")
        
        return results

def main():
    """Main execution with intelligent extraction"""
    try:
        print("🧠 Starting intelligent golf event extraction...")
        
        extractor = SmartGolfEventExtractor()
        
        # Extract events intelligently
        events = extractor.scrape_all_courses()
        
        # Save detailed results
        results = extractor.save_intelligent_results()
        
        # Print summary
        total_events = sum(c['events_found'] for c in events)
        print(f"\n🎯 INTELLIGENT EXTRACTION RESULTS:")
        print(f"✅ Courses with detailed events: {len(events)}")
        print(f"📋 Total events extracted: {total_events}")
        print(f"❌ Errors: {len(extractor.errors)}")
        
        if events:
            print(f"\n🎉 Successfully extracted detailed event information!")
            print(f"📄 Check the JSON file for complete details and formatted Wix post.")
        else:
            print(f"\n🔍 No detailed events extracted this scan.")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        # Ensure file exists for GitHub Actions
        with open('golf_events_results.json', 'w') as f:
            json.dump({'error': str(e), 'timestamp': datetime.now().isoformat()}, f)

if __name__ == "__main__":
    main()
