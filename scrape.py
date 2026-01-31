import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_course_page(url):
    """
    Scrape the CS444/ECE494 Deep Learning for Computer Vision course page
    and extract all important information.
    """
    # Fetch the webpage
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Initialize data structure
    course_info = {
        'url': url,
        'scraped_at': datetime.now().isoformat(),
        'course_title': '',
        'instructor': {},
        'teaching_assistants': [],
        'lecture_info': {},
        'prerequisites': '',
        'overview': '',
        'grading_scheme': {},
        'schedule': [],
        'quick_links': {}
    }
    
    # Extract course title (usually in h1)
    title_tag = soup.find('h1')
    if title_tag:
        course_info['course_title'] = title_tag.get_text(strip=True)
    
    # Extract all paragraphs and sections
    text_content = soup.get_text()
    
    # Extract instructor information
    if 'Instructor:' in text_content:
        instructor_section = text_content.split('Instructor:')[1].split('\n')[0]
        course_info['instructor']['raw'] = instructor_section.strip()
        # Try to extract name and email
        if '(' in instructor_section and ')' in instructor_section:
            name = instructor_section.split('(')[0].strip()
            email = instructor_section.split('(')[1].split(')')[0].strip()
            course_info['instructor']['name'] = name
            course_info['instructor']['email'] = email
    
    # Extract TAs
    if 'TAs:' in text_content:
        ta_section = text_content.split('TAs:')[1].split('\n')[0]
        course_info['teaching_assistants'] = [ta.strip() for ta in ta_section.split(',')]
    
    # Extract lecture information
    if 'Lectures:' in text_content:
        lecture_section = text_content.split('Lectures:')[1].split('\n')[0]
        course_info['lecture_info']['raw'] = lecture_section.strip()
    
    # Extract prerequisites
    if 'Prerequisites:' in text_content:
        prereq_section = text_content.split('Prerequisites:')[1].split('\n')[0]
        course_info['prerequisites'] = prereq_section.strip()
    
    # Extract overview
    if 'Overview:' in text_content:
        overview_section = text_content.split('Overview:')[1].split('Instructor:')[0]
        course_info['overview'] = overview_section.strip()
    
    # Extract schedule from table
    schedule_table = soup.find('table')
    if schedule_table:
        rows = schedule_table.find_all('tr')[1:]  # Skip header row
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                schedule_entry = {
                    'date': cols[0].get_text(strip=True),
                    'topic': cols[1].get_text(strip=True),
                    'assignments': cols[2].get_text(strip=True)
                }
                
                # Extract links from topic column
                links = cols[1].find_all('a')
                if links:
                    schedule_entry['links'] = [
                        {'text': link.get_text(strip=True), 'url': link.get('href')}
                        for link in links
                    ]
                
                course_info['schedule'].append(schedule_entry)
    
    # Extract grading scheme
    grading_tables = soup.find_all('table')
    if len(grading_tables) > 1:
        grading_table = grading_tables[1]
        grading_rows = grading_table.find_all('tr')[1:]
        
        three_credit = {}
        four_credit = {}
        
        for row in grading_rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                category = cols[0].get_text(strip=True)
                three_credit[category] = cols[1].get_text(strip=True)
                four_credit[category] = cols[2].get_text(strip=True)
        
        course_info['grading_scheme']['3_credits'] = three_credit
        course_info['grading_scheme']['4_credits'] = four_credit
    
    # Extract quick links
    links = soup.find_all('a')
    important_links = {}
    for link in links:
        href = link.get('href')
        text = link.get_text(strip=True)
        if href and text:
            if 'policies' in href.lower():
                important_links['policies'] = href
            elif 'mediaspace' in href or 'video' in text.lower():
                important_links['lecture_videos'] = href
            elif 'canvas' in href:
                important_links['canvas'] = href
            elif 'campuswire' in href:
                important_links['campuswire'] = href
    
    course_info['quick_links'] = important_links
    
    # Extract exam dates
    exams = []
    for entry in course_info['schedule']:
        if 'exam' in entry['topic'].lower() or 'exam' in entry['assignments'].lower():
            exams.append({
                'date': entry['date'],
                'description': entry['assignments'] if 'exam' in entry['assignments'].lower() else entry['topic']
            })
    course_info['exams'] = exams
    
    # Extract assignments
    assignments = []
    for entry in course_info['schedule']:
        if 'assignment' in entry['assignments'].lower():
            assignments.append({
                'date': entry['date'],
                'assignment': entry['assignments']
            })
    course_info['assignments'] = assignments
    
    return course_info


def main():
    url = "https://slazebni.cs.illinois.edu/spring26/"
    
    print(f"Scraping {url}...")
    
    try:
        course_data = scrape_course_page(url)
        
        # Save to JSON file
        output_file = 'course_info.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(course_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Successfully scraped course information!")
        print(f"✓ Data saved to {output_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("COURSE SUMMARY")
        print("="*60)
        print(f"\nTitle: {course_data['course_title']}")
        print(f"\nInstructor: {course_data['instructor'].get('name', 'N/A')}")
        print(f"Email: {course_data['instructor'].get('email', 'N/A')}")
        print(f"\nLecture: {course_data['lecture_info'].get('raw', 'N/A')}")
        print(f"\nPrerequisites: {course_data['prerequisites']}")
        
        print(f"\n\nSchedule Entries: {len(course_data['schedule'])}")
        print(f"Assignments: {len(course_data['assignments'])}")
        print(f"Exams: {len(course_data['exams'])}")
        
        print("\n\nAssignments:")
        for assignment in course_data['assignments']:
            print(f"  - {assignment['date']}: {assignment['assignment']}")
        
        print("\n\nExams:")
        for exam in course_data['exams']:
            print(f"  - {exam['date']}: {exam['description']}")
        
        print("\n\nQuick Links:")
        for key, value in course_data['quick_links'].items():
            print(f"  - {key}: {value}")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
