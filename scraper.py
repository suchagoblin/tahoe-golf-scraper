import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
import time
import traceback
import sys

class RobustGolfEventScraper:
    def __init__(self):
        self.events = []
        self.errors = []
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
            
            # Truckee Area
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
        
        # Shorter keyword list for better performance
        self.event_keywords = [
            'tournament', 'scramble', 'camp', 'junior', 'lesson', 
            'league', 'clinic', 'instruction', 'event', 'championship',
            'outing', 'register', 'sign up', 'golf school'
        ]
    
    def scrape_course_safely(self, course_name, course_info):
        """Scrape a single course with comprehensive error handling"""
        try:
            print(f"🏌️ Starting {course_name}...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Single URL attempt with shorter timeout
            try:
                print(f"  Connecting to {course_info['url']}...")
                response = requests.get(
                    course_info['url'], 
                    headers=headers, 
                    timeout=10,  # Reduced timeout
                    allow_redirects=True
                )
                print(f"  Response code: {response.status_code}")
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    page_text = soup.get_text().lower()
                    
                    # Simple keyword search
                    found_keywords = []
                    for keyword in self.event_keywords:
                        if keyword in page_text:
                            found_keywords.append(keyword)
                    
                    if found_keywords:
                        print(f"  ✅ Found keywords: {', '.join(found_keywords[:3])}")
                        
                        # Get a sample of text around keywords
                        sample_text = page_text[:1000] + "..."
                        
                        self.events.append({
                            'course': course_name,
                            'location': course_info['location'],
                            'phone': course_info['phone'],
                            'url': course_info['url'],
                            'keywords_found': found_keywords[:5],
                            'sample_text': sample_text,
                            'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M UTC'),
                            'status': 'success'
                        })
                    else:
                        print(f"  ❌ No event keywords found")
                        self.events.append({
                            'course': course_name,
                            'location': course_info['location'],
                            'phone': course_info['phone'],
                            'url': course_info['url'],
                            'keywords_found': [],
                            'status': 'no_events',
                            'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M UTC')
                        })
                else:
                    print(f"  ❌ HTTP {response.status_code}")
                    self.record_error(course_name, f"HTTP {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print(f"  ❌ Timeout after 10 seconds")
                self.record_error(course_name, "Timeout")
                
            except requests.exceptions.RequestException as e:
                print(f"  ❌ Request failed: {str(e)[:50]}")
                self.record_error(course_name, f"Request error: {str(e)[:50]}")
                
        except Exception as e:
            print(f"  ❌ Unexpected error: {str(e)[:50]}")
            self.record_error(course_name, f"Unexpected error: {str(e)[:50]}")
        
        # Always pause between requests
        time.sleep(2)
    
    def record_error(self, course_name, error_msg):
        """Record errors for debugging"""
        self.errors.append({
            'course': course_name,
            'error': error_msg,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M UTC')
        })
    
    def scrape_all_courses(self):
        """Scrape all courses with progress tracking"""
        total_courses = len(self.courses)
        
        print(f"🏌️ ROBUST GOLF SCRAPER - LAKE TAHOE")
        print("=" * 50)
        print(f"Checking {total_courses} courses...")
        print("=" * 50)
        
        for i, (course_name, course_info) in enumerate(self.courses.items(), 1):
            print(f"\n[{i}/{total_courses}] Processing {course_name}...")
            self.scrape_course_safely(course_name, course_info)
            
            # Progress update
            if i % 3 == 0:
                print(f"\n📊 Progress: {i}/{total_courses} completed")
        
        print("\n" + "=" * 50)
        print("✅ All courses processed!")
        return self.events
    
    def create_summary_report(self):
        """Create a comprehensive summary"""
        successful_scrapes = [e for e in self.events if e.get('status') == 'success']
        no_events = [e for e in self.events if e.get('status') == 'no_events']
        
        report = {
            'scrape_summary': {
                'total_courses': len(self.courses),
                'successful_scrapes': len(successful_scrapes),
                'courses_with_events': len(successful_scrapes),
                'courses_without_events': len(no_events),
                'errors': len(self.errors),
                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M UTC')
            },
            'courses_with_events': successful_scrapes,
            'courses_without_events': no_events,
            'errors': self.errors,
            'all_results': self.events
        }
        
        return report
    
    def save_results(self):
        """Save results with guaranteed file creation"""
        try:
            report = self.create_summary_report()
            
            # Always create the JSON file, even if empty
            with open('golf_events_results.json', 'w') as f:
                json.dump(report, f, indent=2)
            print("✅ Results saved to golf_events_results.json")
            
            # Create a simple text summary
            summary_text = f"""LAKE TAHOE GOLF SCRAPER RESULTS
Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p UTC')}

SUMMARY:
• Total courses checked: {len(self.courses)}
• Courses with events: {len([e for e in self.events if e.get('status') == 'success'])}
• Courses without events: {len([e for e in self.events if e.get('status') == 'no_events'])}
• Errors encountered: {len(self.errors)}

COURSES WITH EVENTS:
"""
            
            successful = [e for e in self.events if e.get('status') == 'success']
            if successful:
                for course in successful:
                    keywords = ', '.join(course['keywords_found'][:3])
                    summary_text += f"• {course['course']} ({course['location']}) - Keywords: {keywords}\n"
            else:
                summary_text += "• None found this scan\n"
            
            if self.errors:
                summary_text += f"\nERRORS:\n"
                for error in self.errors:
                    summary_text += f"• {error['course']}: {error['error']}\n"
            
            with open('scraper_summary.txt', 'w') as f:
                f.write(summary_text)
            print("✅ Summary saved to scraper_summary.txt")
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving results: {e}")
            # Create minimal file to prevent GitHub Actions error
            with open('golf_events_results.json', 'w') as f:
                json.dump({'error': f'Failed to save: {str(e)}'}, f)
            return False

def main():
    """Main execution with comprehensive error handling"""
    try:
        print("Starting robust golf event scraper...")
        
        scraper = RobustGolfEventScraper()
        
        # Scrape all courses
        results = scraper.scrape_all_courses()
        
        # Always save results
        scraper.save_results()
        
        # Print final summary
        successful = len([e for e in results if e.get('status') == 'success'])
        print(f"\n🎯 FINAL RESULTS:")
        print(f"✅ Courses with events: {successful}")
        print(f"📊 Total courses checked: {len(scraper.courses)}")
        print(f"❌ Errors: {len(scraper.errors)}")
        
        if successful > 0:
            print(f"\n🎉 Found golf events! Check the JSON file for details.")
        else:
            print(f"\n🔍 No events found, but all courses were checked.")
            print(f"This could mean courses don't have current events posted online.")
        
    except Exception as e:
        print(f"❌ Critical error in main(): {e}")
        traceback.print_exc()
        
        # Ensure we always create the required file
        try:
            with open('golf_events_results.json', 'w') as f:
                json.dump({
                    'critical_error': str(e),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M UTC')
                }, f, indent=2)
        except:
            pass
        
        sys.exit(1)

if __name__ == "__main__":
    main()
