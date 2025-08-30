- name: Upload results as artifact
          uses: actions/upload-artifact@v4
          with:
            name: golf-events-results
            path: |
              golf_events_results.json
              READY_TO_PASTE.txt
              scraper_summary.txt
            retention-days: 30import requests
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
                'location': 'South Lake Tahoe',
                'phone': '(530) 577-0788'
            },
            'Northstar Golf Course': {
                'urls': [
                    'https://www.northstarcalifornia.com/golf',
                    'https://www.northstarcalifornia.com'
                ],
                'location': 'Truckee',
                'phone': '(530) 562-2490'
            },
            'Coyote Moon Golf Course': {
                'urls': [
                    'https://www.coyotemoon.com',
                    'https://www.coyotemoon.com/golf'
                ],
                'location': 'Truckee',
                'phone': '(530) 587-0886'
            }
        }
        
        # Comprehensive golf keywords
        self.golf_keywords = [
            'golf tournament', 'tournament', 'scramble', 'golf camp', 'junior golf', 
            'golf lesson', 'lesson', 'golf league', 'league', 'golf clinic', 'clinic',
            'golf instruction', 'instruction', 'golf championship', 'pga', 'golf pro',
            'golf program', 'golf school', 'tee time', 'golf event'
        ]
    
    def extract_event_info(self, text_chunk):
        """Extract event details from a text chunk"""
        details = {
            'text': text_chunk.strip(),
            'dates': [],
            'times': [],
            'prices': [],
            'ages': [],
            'contact': []
        }
        
        text_lower = text_chunk.lower()
        
        # Extract dates - more patterns
        date_patterns = [
            r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(?:st|nd|rd|th)?(?:\s*[-–]\s*\d{1,2}(?:st|nd|rd|th)?)?\s*(?:,\s*)?\d{0,4}',
            r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\.?\s+\d{1,2}(?:\s*[-–]\s*\d{1,2})?',
            r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',
            r'\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)s?',
            r'(?:daily|weekly|monthly)',
            r'(?:spring|summer|fall|winter)\s*(?:20\d{2}|\d{2})?'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text_lower)
            details['dates'].extend(matches)
        
        # Extract times
        time_patterns = [
            r'\d{1,2}:\d{2}\s*(?:am|pm)?',
            r'\d{1,2}\s*(?:am|pm)',
            r'\b(?:morning|afternoon|evening|noon)\b'
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, text_lower)
            details['times'].extend(matches)
        
        # Extract prices
        price_patterns = [
            r'\$\d+(?:\.\d{2})?(?:\s*per\s*\w+)?',
            r'(?:cost|fee|price)s?[:s]?\s*\$?\d+',
            r'\d+\s*dollars?',
            r'free\b',
            r'no\s+(?:cost|charge|fee)'
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, text_lower)
            details['prices'].extend(matches)
        
        # Extract age/skill info
        age_patterns = [
            r'ages?\s+\d+(?:\s*[-–to]+\s*\d+)?',
            r'\d+(?:\s*[-–to]+\s*\d+)?\s+years?\s+old',
            r'\b(?:junior|adult|senior|youth|kids?|children)\b',
            r'\b(?:beginner|intermediate|advanced|all\s+levels)\b'
        ]
        
        for pattern in age_patterns:
            matches = re.findall(pattern, text_lower)
            details['ages'].extend(matches)
        
        # Extract contact info
        contact_patterns = [
            r'\(\d{3}\)\s*\d{3}[-.\s]*\d{4}',
            r'\d{3}[-.\s]*\d{3}[-.\s]*\d{4}',
            r'[\w.-]+@[\w.-]+\.\w+',
            r'pro\s*shop',
            r'(?:call|contact|register)'
        ]
        
        for pattern in contact_patterns:
            matches = re.findall(pattern, text_lower)
            details['contact'].extend(matches)
        
        return details
    
    def scrape_course_comprehensive(self, course_name, course_info):
        """Comprehensive scraping with multiple fallbacks"""
        print(f"🏌️ Comprehensively scanning {course_name}...")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5'
            }
            
            found_events = []
            
            # Try each URL for this course
            for url in course_info['urls']:
                try:
                    print(f"  Checking: {url}")
                    response = requests.get(url, headers=headers, timeout=15)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Remove noise
                        for noise in soup(['script', 'style', 'nav', 'footer', 'header']):
                            noise.decompose()
                        
                        # Get all text content
                        all_text = soup.get_text()
                        
                        # Split into chunks (paragraphs)
                        chunks = [chunk.strip() for chunk in re.split(r'\n\s*\n', all_text) if chunk.strip()]
                        
                        # Analyze each chunk
                        for chunk in chunks:
                            if len(chunk) < 30 or len(chunk) > 800:  # Skip too short or too long
                                continue
                            
                            chunk_lower = chunk.lower()
                            
                            # Check for golf keywords
                            found_golf_keywords = [kw for kw in self.golf_keywords if kw in chunk_lower]
                            
                            if found_golf_keywords:
                                # Must also contain some golf context
                                golf_context = ['golf', 'course', 'pro', 'tee', 'green', 'fairway', 'swing', 'club']
                                has_golf_context = any(context in chunk_lower for context in golf_context)
                                
                                # Exclude obvious non-golf content
                                exclude_terms = ['sailing', 'tennis', 'swimming', 'hiking', 'skiing', 'restaurant', 'dining']
                                has_exclude = any(term in chunk_lower for term in exclude_terms)
                                
                                if has_golf_context and not has_exclude:
                                    print(f"    ✅ Found potential golf event: {found_golf_keywords}")
                                    
                                    # Extract detailed info
                                    event_details = self.extract_event_info(chunk)
                                    
                                    # Score relevance
                                    relevance = len(found_golf_keywords) + len(event_details['dates']) + len(event_details['prices'])
                                    
                                    found_events.append({
                                        'title': chunk[:100] + '...' if len(chunk) > 100 else chunk[:50],
                                        'keywords': found_golf_keywords,
                                        'details': event_details,
                                        'source_url': url,
                                        'relevance_score': relevance
                                    })
                        
                        if found_events:
                            print(f"    Found {len(found_events)} golf-related sections")
                            break  # Found events, don't need to check more URLs
                    
                    time.sleep(2)  # Be respectful
                    
                except requests.exceptions.RequestException as e:
                    print(f"    ❌ Failed to load {url}: {str(e)[:50]}")
                    continue
            
            # Process results
            if found_events:
                # Sort by relevance and take top 3
                found_events.sort(key=lambda x: x['relevance_score'], reverse=True)
                top_events = found_events[:3]
                
                self.events.append({
                    'course': course_name,
                    'location': course_info['location'],
                    'phone': course_info['phone'],
                    'main_url': course_info['urls'][0],
                    'events_found': len(found_events),
                    'top_events': top_events,
                    'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M UTC'),
                    'status': 'success'
                })
                
                print(f"  ✅ Successfully extracted {len(found_events)} golf events")
            else:
                print(f"  ❌ No golf events found")
                self.record_error(course_name, "No golf events found")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            self.record_error(course_name, str(e)[:100])
    
    def record_error(self, course_name, error_msg):
        """Record errors"""
        self.errors.append({
            'course': course_name,
            'error': error_msg,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M UTC')
        })
    
    def scrape_all_courses(self):
        """Scrape all courses"""
        print("🏌️ FIXED GOLF EVENT SCRAPER - LAKE TAHOE")
        print("=" * 50)
        
        for i, (course_name, course_info) in enumerate(self.courses.items(), 1):
            print(f"\n[{i}/{len(self.courses)}] {course_name}...")
            self.scrape_course_comprehensive(course_name, course_info)
        
        print("\n" + "=" * 50)
        print(f"✅ Scraping complete!")
        print(f"Courses with events: {len(self.events)}")
        return self.events
    
    def format_for_wix(self):
        """Format events for Wix posting"""
        if not self.events:
            return """🏌️ **Lake Tahoe Golf Course Check - No Current Events Found**
*Updated: {}*

We checked 5 major golf courses in the Lake Tahoe area but didn't find any current golf events, programs, or tournaments posted online at this time.

**Courses Checked:**
• Edgewood Tahoe (South Lake Tahoe)
• Tahoe Donner Golf Course (Truckee) 
• Lake Tahoe Golf Course (South Lake Tahoe)
• Northstar Golf Course (Truckee)
• Coyote Moon Golf Course (Truckee)

**What This Means:**
• Courses may not have current events posted on their websites
• Events might be listed in booking systems or social media only
• It's still worth calling courses directly for upcoming programs

**Next Steps for Slicer Golf Club Community:**
📞 **Call courses directly** to ask about:
- Upcoming tournaments or scrambles
- Junior golf programs for summer 2025
- Adult lessons and clinics
- Corporate outing opportunities

**Pro Tip:** Mention you're from the Slicer Golf Club community - they may be interested in equipment demos or partnerships!

*We'll continue monitoring these courses and update you when new programs are announced.*""".format(datetime.now().strftime('%B %d, %Y'))
        
        post_content = f"""🏌️ **Golf Events & Programs - Lake Tahoe Area**
*Updated: {datetime.now().strftime('%B %d, %Y')} | {len(self.events)} courses with events*

Great opportunities for Slicer Golf Club enthusiasts! 🏌️‍♂️

"""
        
        for course_data in self.events:
            post_content += f"## 📍 **{course_data['course']}** ({course_data['location']})\n"
            post_content += f"📞 {course_data['phone']} | 🌐 {course_data['main_url']}\n\n"
            
            for i, event in enumerate(course_data['top_events'], 1):
                post_content += f"### {i}. Golf Program/Event Found\n"
                post_content += f"**Keywords:** {', '.join(event['keywords'])}\n"
                
                details = event['details']
                
                if details['dates']:
                    post_content += f"📅 **Dates:** {', '.join(list(set(details['dates'][:3])))}\n"
                
                if details['times']:
                    post_content += f"🕐 **Times:** {', '.join(list(set(details['times'][:3])))}\n"
                
                if details['prices']:
                    post_content += f"💰 **Pricing:** {', '.join(list(set(details['prices'][:3])))}\n"
                
                if details['ages']:
                    post_content += f"👥 **Ages/Level:** {', '.join(list(set(details['ages'][:3])))}\n"
                
                post_content += f"📄 **Details:** {event['details']['text'][:200]}...\n\n"
            
            post_content += "---\n\n"
        
        post_content += """💡 **Take Action!** These are real opportunities:
- Call the courses to get full program details
- Ask about equipment demos with Slicer Golf Clubs
- Inquire about group rates for our community
- Sign up for programs that match your skill level

📧 **Planning to participate?** Let us know in the comments!

*Automatically found golf-related content across the Lake Tahoe region.*"""
        
        return post_content
    
    def save_results(self):
        """Save results in both JSON and clean text formats"""
        results = {
            'scrape_summary': {
                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M UTC'),
                'courses_checked': len(self.courses),
                'courses_with_events': len(self.events),
                'total_events_found': sum(c['events_found'] for c in self.events),
                'method': 'comprehensive_golf_focused'
            },
            'detailed_events': self.events,
            'errors': self.errors,
            'wix_community_post': self.format_for_wix()
        }
        
        # Save JSON results (for technical analysis)
        with open('golf_events_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        # Save clean text version (for easy copy-paste)
        clean_post_content = self.format_for_wix()
        with open('READY_TO_PASTE.txt', 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("SLICER GOLF CLUB - WIX GROUPS POST\n")
            f.write("READY TO COPY & PASTE\n")
            f.write("=" * 60 + "\n\n")
            f.write(clean_post_content)
            f.write("\n\n" + "=" * 60 + "\n")
            f.write("INSTRUCTIONS:\n")
            f.write("1. Select ALL text above the instructions\n")
            f.write("2. Copy it (Ctrl+C or Cmd+C)\n")
            f.write("3. Go to your Wix Groups\n")
            f.write("4. Create New Post\n")
            f.write("5. Paste the content\n")
            f.write("6. Add any personal comments\n")
            f.write("7. Post to your community!\n")
            f.write("=" * 60 + "\n")
        
        # Save a summary for quick review
        summary_content = f"""LAKE TAHOE GOLF SCRAPER SUMMARY
Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p UTC')}

RESULTS:
• Courses checked: {len(self.courses)}
• Courses with golf events: {len(self.events)}
• Total golf programs found: {sum(c['events_found'] for c in self.events)}

FILES CREATED:
• golf_events_results.json (detailed technical data)
• READY_TO_PASTE.txt (clean content for Wix Groups)
• scraper_summary.txt (this file)

"""
        
        if self.events:
            summary_content += "COURSES WITH GOLF PROGRAMS:\n"
            for course in self.events:
                summary_content += f"• {course['course']} ({course['location']}) - {course['events_found']} programs\n"
        else:
            summary_content += "No golf programs found this scan.\n"
            
        if self.errors:
            summary_content += f"\nISSUES ENCOUNTERED:\n"
            for error in self.errors:
                summary_content += f"• {error['course']}: {error['error']}\n"
        
        with open('scraper_summary.txt', 'w') as f:
            f.write(summary_content)
        
        print("✅ Results saved in multiple formats:")
        print("   📄 golf_events_results.json (technical data)")
        print("   📋 READY_TO_PASTE.txt (clean Wix Groups post)")
        print("   📊 scraper_summary.txt (quick overview)")
        
        return results

def main():
    """Main execution"""
    try:
        scraper = FixedGolfEventScraper()
        events = scraper.scrape_all_courses()
        results = scraper.save_results()
        
        total_events = sum(c['events_found'] for c in events)
        print(f"\n🎯 FINAL RESULTS:")
        print(f"Courses with golf events: {len(events)}")
        print(f"Total golf events found: {total_events}")
        print(f"Errors: {len(scraper.errors)}")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        with open('golf_events_results.json', 'w') as f:
            json.dump({'error': str(e), 'timestamp': datetime.now().isoformat()}, f)

if __name__ == "__main__":
    main()
