class HealthMetricsCalculator:
    """Calculates and categorizes body mass index measurements."""
    
    @staticmethod
    def compute_body_mass_index(weight_kg, height_m):
        """
        Calculate BMI from weight and height.
        
        Args:
            weight_kg: Body weight in kilograms
            height_m: Body height in meters
            
        Returns:
            BMI value as float
            
        Raises:
            ValueError: If height is zero or negative
        """
        if height_m <= 0:
            raise ValueError("Height must be a positive value")
        
        bmi_result = weight_kg / (height_m * height_m)
        return bmi_result
    
    @staticmethod
    def determine_health_category(bmi_value):
        """
        Classify BMI into health categories.
        
        Args:
            bmi_value: Calculated BMI
            
        Returns:
            Category string
        """
        if bmi_value < 18.5:
            return "Underweight"
        elif bmi_value < 25:
            return "Normal weight"
        elif bmi_value < 30:
            return "Overweight"
        else:
            return "Obese"
