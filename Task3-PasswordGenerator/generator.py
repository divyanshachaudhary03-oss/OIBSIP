import secrets
import string

class SecurePasswordBuilder:
    """
    A secure password generation utility that creates customizable passwords
    with configurable character sets and strength evaluation.
    """
    
    def __init__(self):
        # Store character sets in a dictionary for flexible access
        self.char_sets = {
            'upper': string.ascii_uppercase,
            'lower': string.ascii_lowercase,
            'numbers': string.digits,
            'special': '!@#$%^&*()_+-=[]{}|;:,.<>?'
        }
    
    def build_password(self, pwd_length=12, include_upper=True, include_lower=True, 
                      include_numbers=True, include_special=True, forbidden_chars=""):
        """
        Constructs a secure password based on specified parameters.
        
        Args:
            pwd_length: Desired password length
            include_upper: Whether to include uppercase letters
            include_lower: Whether to include lowercase letters
            include_numbers: Whether to include numeric digits
            include_special: Whether to include special symbols
            forbidden_chars: String of characters to exclude from generation
            
        Returns:
            Generated password string or error message
        """
        # Validate that at least one character type is selected
        if not any([include_upper, include_lower, include_numbers, include_special]):
            return "Error: At least one character type must be selected."
        
        # Build available character pools after applying exclusions
        available_pools = {}
        
        if include_upper:
            filtered = ''.join(ch for ch in self.char_sets['upper'] if ch not in forbidden_chars)
            if filtered:
                available_pools['upper'] = filtered
            else:
                return "Error: All uppercase letters have been excluded."
        
        if include_lower:
            filtered = ''.join(ch for ch in self.char_sets['lower'] if ch not in forbidden_chars)
            if filtered:
                available_pools['lower'] = filtered
            else:
                return "Error: All lowercase letters have been excluded."
        
        if include_numbers:
            filtered = ''.join(ch for ch in self.char_sets['numbers'] if ch not in forbidden_chars)
            if filtered:
                available_pools['numbers'] = filtered
            else:
                return "Error: All numbers have been excluded."
        
        if include_special:
            filtered = ''.join(ch for ch in self.char_sets['special'] if ch not in forbidden_chars)
            if filtered:
                available_pools['special'] = filtered
            else:
                return "Error: All special characters have been excluded."
        
        # Ensure we have at least some characters to work with
        if not available_pools:
            return "Error: No characters available after applying exclusions."
        
        # Create password by ensuring diversity first
        pwd_chars = []
        pool_keys = list(available_pools.keys())
        
        # Guarantee at least one character from each enabled pool
        for pool_name in pool_keys:
            pwd_chars.append(secrets.choice(available_pools[pool_name]))
        
        # Combine all available characters for remaining slots
        combined_pool = ''.join(available_pools.values())
        
        # Fill remaining positions with random characters from combined pool
        chars_needed = pwd_length - len(pwd_chars)
        if chars_needed > 0:
            for _ in range(chars_needed):
                pwd_chars.append(secrets.choice(combined_pool))
        
        # Shuffle to eliminate predictable patterns
        secrets.SystemRandom().shuffle(pwd_chars)
        
        return ''.join(pwd_chars)
    
    def evaluate_strength(self, pwd):
        """
        Evaluates password strength and returns a rating with color code.
        
        Args:
            pwd: Password string to evaluate
            
        Returns:
            Tuple of (strength_label, color_hex)
        """
        strength_points = 0
        
        # Length-based scoring
        if len(pwd) >= 8:
            strength_points += 1
        if len(pwd) >= 12:
            strength_points += 1
        if len(pwd) >= 16:
            strength_points += 1
        
        # Character diversity scoring
        has_upper = any(ch in self.char_sets['upper'] for ch in pwd)
        has_lower = any(ch in self.char_sets['lower'] for ch in pwd)
        has_numbers = any(ch in self.char_sets['numbers'] for ch in pwd)
        has_special = any(ch in self.char_sets['special'] for ch in pwd)
        
        diversity_count = sum([has_upper, has_lower, has_numbers, has_special])
        strength_points += diversity_count
        
        # Map points to strength categories
        if strength_points <= 2:
            return "Weak", "#e74c3c"  # Red
        elif strength_points <= 4:
            return "Moderate", "#f39c12"  # Orange
        elif strength_points <= 6:
            return "Strong", "#2ecc71"  # Green
        else:
            return "Very Strong", "#27ae60"  # Dark Green
