import boto3
import re

class EntityRecognitionService:
    def __init__(self):
        self.comprehend = boto3.client('comprehend', region_name='us-east-1')

    def extract_entities(self, text):
        """Extract and label entities from text"""
        print(f"Input text for entity extraction: {text[:200]}...")  # Log first 200 chars
        
        entities = {
            'first_name': '',
            'last_name': '',
            'unit_number': '',
            'full_address': '',
            'tracking_number': ''
        }
        
        # AWS Comprehend for person names and locations
        response = self.comprehend.detect_entities(Text=text, LanguageCode='en')
        print(f"Comprehend detected entities: {response['Entities']}")
        
        names = []
        addresses = []
        
        for entity in response['Entities']:
            if entity['Type'] == 'PERSON':
                names.append(entity['Text'])
            elif entity['Type'] == 'LOCATION':
                addresses.append(entity['Text'])
        
        print(f"Extracted names: {names}")
        print(f"Extracted addresses: {addresses}")
        
        # Extract first/last name from detected names
        if names:
            name_parts = names[0].split()
            entities['first_name'] = name_parts[0] if len(name_parts) > 0 else ''
            entities['last_name'] = name_parts[-1] if len(name_parts) > 1 else ''
        
        # Extract tracking number
        entities['tracking_number'] = self._extract_tracking_number(text)
        print(f"Extracted tracking number: {entities['tracking_number']}")
        
        # Extract unit number and full address
        entities['unit_number'], entities['full_address'] = self._extract_address_info(text)
        print(f"Extracted unit number: {entities['unit_number']}")
        print(f"Extracted full address: {entities['full_address']}")
        
        print(f"Final entities: {entities}")
        return entities
    
    def _extract_tracking_number(self, text):
        """Extract tracking numbers using regex patterns"""
        print(f"Searching for tracking number in text: {text.replace(' ', '')}")
        
        patterns = [
            r'1Z[0-9A-Z]{16}',  # UPS
            r'\b\d{12,14}\b',   # FedEx
            r'\b\d{20,22}\b',    # USPS
            r'TBC[0-9]{12}'     # Amazon
        ]
        
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, text.replace(' ', ''))
            if match:
                print(f"Tracking number found with pattern {i}: {match.group()}")
                return match.group()
        
        print("No tracking number found")
        return ''
    
    def _extract_address_info(self, text):
        """Extract unit number and full address"""
        print(f"Extracting address info from text lines: {text.split('\n')}")
        
        lines = text.split('\n')
        
        # Filter out lines with shipping codes and metadata (keep TBC for tracking)
        filtered_lines = []
        for line in lines:
            line_clean = line.strip()
            # Skip lines with shipping codes, weights, dates, or long mixed data
            if (re.search(r'\b[A-Z]{3}\d+\b', line_clean) or  # YYZ1, DON8
                re.search(r'\d+\.\d+\s*Lbs', line_clean) or    # 2.2 Lbs
                re.search(r'\d{2}/\d{2}', line_clean) or       # 04/21
                re.search(r'CYCLE\s*\d+', line_clean) or      # CYCLE 1
                len(line_clean.split()) > 15):               # Very long lines with mixed data
                continue
            filtered_lines.append(line_clean)
        
        lines = filtered_lines
        print(f"Filtered lines: {lines}")
        unit_number = ''
        full_address = ''
        
        # Define address indicators first
        address_indicators = ['street', 'st', 'avenue', 'ave', 'road', 'rd', 'drive', 'dr','boulevard','blvd','lane','ln','court','ct','way','wy','place','pl','square','sq','trail','trl','parkway','pkwy','circle','cir','loop','ne','nw','se','sw','n','s','e','w']
        zip_pattern = r'\b\d{5}(?:-\d{4})?\b'
        
        # Look for unit/apt patterns
        unit_pattern = r'(?:unit|apt|apartment|suite|ste)\s*#?(\w+)'
        unit_match = re.search(unit_pattern, text, re.IGNORECASE)
        if unit_match:
            unit_number = unit_match.group(1)
            print(f"Unit number found with pattern: {unit_number}")
        
        # Extract unit number and full address from street address line
        if not unit_number:
            print("No unit pattern found, checking address lines...")
            # Pattern: unit_number - street_number street_name (320-4628 Kingston Rd)
            unit_dash_match = re.search(r'(\d+[A-Z]?)\s*-\s*(\d+)\s+([A-Za-z][^\n,]+)', text)
            if unit_dash_match:
                unit_number = unit_dash_match.group(1)
                street_number = unit_dash_match.group(2)
                street_name = unit_dash_match.group(3).strip()
                full_address = f"{street_number} {street_name}"
                print(f"Dash pattern - Unit: {unit_number}, Street: {full_address}")
            else:
                # Pattern: street_number street_name unit_number (735 Don Mills Road 2003)
                address_match = re.search(r'(\d+)\s+([A-Za-z\s]+(?:Road|Street|Ave|Avenue|Dr|Drive|Blvd|Boulevard|Rd|St))\s+(\d+[A-Z]?)', text, re.IGNORECASE)
                if address_match:
                    street_number = address_match.group(1)
                    street_name = address_match.group(2).strip()
                    unit_number = address_match.group(3)
                    full_address = f"{street_number} {street_name}"
                    print(f"Direct extraction - Street: {full_address}, Unit: {unit_number}")
                else:
                    # Fall back to filtered lines
                    for line in lines:
                        line_lower = line.lower()
                        if any(indicator in line_lower for indicator in address_indicators):
                            print(f"Address line found: {line}")
                            street_match = re.search(r'(\d+)\s+([^\d]+?)\s+(\d+[A-Z]?)', line)
                            if street_match:
                                street_number = street_match.group(1)
                                street_name = street_match.group(2).strip()
                                unit_number = street_match.group(3)
                                full_address = f"{street_number} {street_name}"
                                print(f"Pattern 1 - Street: {full_address}, Unit: {unit_number}")
                                break
        
        # If full_address not set above, fall back to joining address lines
        if not full_address:
            address_lines = []
            for line in lines:
                line_lower = line.lower()
                if (any(indicator in line_lower for indicator in address_indicators) or 
                    re.search(zip_pattern, line)):
                    address_lines.append(line.strip())
            full_address = ', '.join(address_lines)
            print(f"Address lines found: {address_lines}")
        
        return unit_number, full_address