from django.utils import timezone
from mainapp.models import Event, Department, CustomUser
from datetime import datetime, timedelta
import random
import sys

# Department data
departments = [
    {'name': 'Computer Science and Engineering', 'code': 'CSE'},
    {'name': 'Electrical Engineering', 'code': 'EE'},
    {'name': 'Mechanical Engineering', 'code': 'ME'},
    {'name': 'Business Administration', 'code': 'BA'},
    {'name': 'Physics', 'code': 'PHY'}
]

# Event data
events = [
    {
        'title': 'Tech Innovation Summit 2024',
        'description': 'A seminar featuring industry leaders discussing the latest technological trends and innovations.',
        'category': 'seminar',
        'tickets': 200
    },
    {
        'title': 'Spring Music Festival',
        'description': 'Annual music festival featuring performances by talented students and guest artists.',
        'category': 'concert',
        'tickets': 500
    },
    {
        'title': 'Engineering Design Showcase',
        'description': 'Exhibition of innovative student projects from various engineering disciplines.',
        'category': 'educational',
        'tickets': 150
    },
    {
        'title': 'Business Leadership Conference',
        'description': 'Interactive sessions with successful entrepreneurs and business leaders.',
        'category': 'seminar',
        'tickets': 300
    },
    {
        'title': 'Cultural Night 2024',
        'description': 'A celebration of diversity through music, dance, and traditional performances.',
        'category': 'stage_event',
        'tickets': 400
    },
    {
        'title': 'Physics Symposium',
        'description': 'Academic conference featuring research presentations and guest lectures.',
        'category': 'educational',
        'tickets': 100
    },
    {
        'title': 'Talent Hunt 2024',
        'description': 'Annual talent competition showcasing student performances across various categories.',
        'category': 'stage_event',
        'tickets': 350
    },
    {
        'title': 'Career Fair Spring 2024',
        'description': 'Connect with leading companies and explore career opportunities.',
        'category': 'other',
        'tickets': 600
    },
    {
        'title': 'Research Excellence Day',
        'description': 'Showcase of groundbreaking research projects from all departments.',
        'category': 'educational',
        'tickets': 250
    },
    {
        'title': 'Alumni Meet 2024',
        'description': 'Annual gathering of alumni sharing experiences and networking opportunities.',
        'category': 'other',
        'tickets': 450
    }
]

# Locations
locations = [
    'Main Auditorium',
    'Conference Hall A',
    'Open Air Theater',
    'Seminar Hall 1',
    'Exhibition Center',
    'Sports Complex',
    'Central Library Hall',
    'Student Center'
]

def create_departments():
    try:
        created_depts = []
        for dept in departments:
            dept_obj, created = Department.objects.get_or_create(
                code=dept['code'],
                defaults={'name': dept['name']}
            )
            created_depts.append(dept_obj)
            print(f"Department {'created' if created else 'found'}: {dept['name']}")
        return created_depts
    except Exception as e:
        print(f"Error creating departments: {str(e)}")
        return []

def create_events(departments):
    try:
        # Get an admin user
        admin_user = CustomUser.objects.filter(role='admin').first()
        if not admin_user:
            print("No admin user found. Please create an admin user first.")
            return

        print(f"Using admin user: {admin_user.username}")

        # Generate events
        start_date = timezone.now() + timedelta(days=1)
        for event in events:
            try:
                # Random date within next 60 days
                event_date = start_date + timedelta(days=random.randint(1, 60))
                # Random time between 9 AM and 6 PM
                hour = random.randint(9, 18)
                minute = random.randint(0, 59)
                event_datetime = timezone.make_aware(datetime.combine(event_date.date(), datetime.strptime(f"{hour}:{minute}", "%H:%M").time()))

                dept = random.choice(departments)
                new_event = Event.objects.create(
                    title=event['title'],
                    description=event['description'],
                    date=event_datetime,
                    location=random.choice(locations),
                    available_tickets=event['tickets'],
                    department=dept,
                    created_by=admin_user,
                    category=event['category']
                )
                print(f"Created event: {new_event.title} in department {dept.name}")
            except Exception as e:
                print(f"Error creating event {event['title']}: {str(e)}")

    except Exception as e:
        print(f"Error in create_events: {str(e)}")

def main():
    try:
        print("Creating departments...")
        departments = create_departments()
        if not departments:
            print("Failed to create departments. Exiting.")
            return

        print("\nCreating events...")
        create_events(departments)
        print("\nScript completed successfully.")

    except Exception as e:
        print(f"Error in main: {str(e)}")

if __name__ == "__main__":
    main()