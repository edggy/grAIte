
class TimelineNode:
    def __init__(self, parent, diff):
        self.parent = parent
        self.diff = diff

class Timeline:
    '''
    This is a tree of Worlds including orphaned branches
    
    Each node has a pointer to it's parent with a diff of the changes
    '''
    
    def __init__(self):
        