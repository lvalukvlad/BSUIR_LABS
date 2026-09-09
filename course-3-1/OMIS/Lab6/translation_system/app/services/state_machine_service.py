from enum import Enum

class UIState(Enum):
    ENTRY = "entry"
    VIEW = "view"
    EDIT = "edit"
    APPROVAL = "approval"
    LOCALIZATION = "localization"

class StateMachineService:
    
    TRANSITIONS = {
        UIState.ENTRY: [UIState.VIEW],
        UIState.VIEW: [UIState.EDIT, UIState.APPROVAL, UIState.LOCALIZATION],
        UIState.EDIT: [UIState.VIEW, UIState.APPROVAL],
        UIState.APPROVAL: [UIState.VIEW, UIState.LOCALIZATION],
        UIState.LOCALIZATION: [UIState.VIEW, UIState.APPROVAL]
    }
    
    def __init__(self, initial_state=UIState.ENTRY):
        self.current_state = initial_state
        self.state_history = [initial_state]
    
    def can_transition(self, target_state):
        return target_state in self.TRANSITIONS.get(self.current_state, [])
    
    def transition(self, target_state):
        if self.can_transition(target_state):
            self.current_state = target_state
            self.state_history.append(target_state)
            return True
        return False
    
    def get_current_state(self):
        return self.current_state
    
    def get_available_transitions(self):
        return self.TRANSITIONS.get(self.current_state, [])
    
    def reset(self):
        self.current_state = UIState.ENTRY
        self.state_history = [UIState.ENTRY]

