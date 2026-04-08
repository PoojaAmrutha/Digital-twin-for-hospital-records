import numpy as np

class PrivacyEngine:
    """
    Simulates a Local Differential Privacy (LDP) mechanism.
    This adds noise to sensitive data before it leaves the 'device' (or in this simulation, before aggregate analysis).
    """
    
    def __init__(self, epsilon=1.0):
        self.epsilon = epsilon
        
    def add_laplace_noise(self, value, sensitivity=1.0):
        """
        Adds Laplace noise to numerical values.
        value: The actual count/metric
        sensitivity: Impact of one individual on the result
        """
        scale = sensitivity / self.epsilon
        noise = np.random.laplace(0, scale)
        return value + noise

    def randomize_response(self, binary_value: bool, p=0.75) -> bool:
        """
        Randomized Response for sensitive binary attributes (e.g., "Has Disease X?").
        Returns a flipped coin version of the truth.
        p: Probability of answering truthfully
        """
        if np.random.random() < p:
            return binary_value
        else:
            return not binary_value

    def apply_ldp_to_stats(self, data_dict):
        """
        Apply LDP to a dictionary of statistics.
        """
        noisy_data = {}
        for key, value in data_dict.items():
            if isinstance(value, (int, float)):
                # Assume sensitivity of 1 for counts/simple metrics
                noisy_data[key] = round(self.add_laplace_noise(value), 1)
            else:
                noisy_data[key] = value
        return noisy_data
