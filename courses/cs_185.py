from bs4 import BeautifulSoup
import json
import sys
from courses.base_course import BaseCourse

class CS_185(BaseCourse):
    """
    Different than other implementations, this class aims to find total open seats for the
    lecture section of CS177. Aims to find total open seat < 10;
    """
    def __init__(self):
        super().__init__("https://classes.berkeley.edu/content/2026-spring-compsci-185-001-lec-001")

    def parse_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')

        # Find the big JSON blob
        script_tag = soup.find('script', attrs={
            'type': 'application/json',
            'data-drupal-selector': 'drupal-settings-json'
        })
        if not script_tag:
            print("Could not find drupal settings JSON.")
            sys.exit(1)

        settings = json.loads(script_tag.string)

        # Drill into the JSON to get the "available" object
        enrollment = settings.get('ucb', {}).get('enrollment', {})
        available = enrollment.get('available', {})
        if not available:
            print("Could not find 'available' enrollment data in JSON.")
            sys.exit(1)

        # Re-use your existing helper
        total_open_seats = self.calculate_total_open_seats(available)
        is_available = total_open_seats > 30  # tweak threshold as you like

        message = f"CS185 Lecture has {total_open_seats} open seats."
        return self.extract_data(json.dumps({'available': available}))
    
    def extract_data(self, data_json):
        try:
            data = json.loads(data_json)
            # enrolled = data.get('available', {}).get('enrollmentStatus', {}).get('enrolledCount', 0)
            total_open_seats = self.calculate_total_open_seats(data.get('available', {}))
            available = total_open_seats > 30
            message = f"CS185 Lecture has {total_open_seats} seats opened!"
            return available, message
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            sys.exit(1)

    @staticmethod
    def calculate_total_open_seats(available):
        """Algorithm to calculate total open seats for UC Berkeley's courses

        Note: it's not a simply max_enroll - enrolled_count
        Below code refers to:
        https://classes.berkeley.edu/sites/default/files/js/js_wkZa4u4BCnSi4JXgkE3Om2OjgDKSaG35ZwAKoHBOzqI.js

        >>> available = {
        ...        'combination': {
        ...            'maxEnrollCombinedSections': 90,
        ...            'enrolledCountCombinedSections': 118
        ...        },
        ...        'enrollmentStatus': {
        ...            'maxEnroll': 74,
        ...            'enrolledCount': 72
        ...        }}
        >>> CS160.calculate_total_open_seats(available)
        0
        """
        if 'combination' in available:
            combined_open_seats = available['combination']['maxEnrollCombinedSections'] - available['combination']['enrolledCountCombinedSections']
            per_class_open_seats = available['enrollmentStatus']['maxEnroll'] - available['enrollmentStatus']['enrolledCount']
            value = min(combined_open_seats, per_class_open_seats)
            return max(value, 0)
        else:
            return max(available['enrollmentStatus']['maxEnroll'] - available['enrollmentStatus']['enrolledCount'], 0)
