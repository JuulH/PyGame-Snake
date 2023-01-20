from math import sqrt, acos, atan2, pi

# Return value between a and b with 0 < c < 1
def lerp(a, b, c):
    return a * (1 - c) + b * c

def Deg2Rad(deg):
    return deg * 0.01745329251

def Rad2Deg(rad):
    return rad / 0.01745329251

class Vector2():
    def __init__(self, x, y):
        self.x = x if x is not None else 0
        self.y = y if y is not None else 0
    
    def __add__(self, other): # Overwrite + operator
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other): # Overwrite - operator
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __mul__(self,f): # Overwrite * operator with dot product
        if isinstance(f, int) or isinstance(f, float):
            return Vector2(self.x * f, self.y * f)
        elif isinstance(f, Vector2):
            return Vector2(self.x * f.x, self.y * f.y)
        else:
            raise TypeError('Wrong type')
    
    def __truediv__ (self, f): # Overwrite / operator
        if isinstance(f, int) or isinstance(f, float):
            return Vector2(self.x / f, self.y / f)
        elif isinstance(f, Vector2):
            return Vector2(self.x / f.x, self.y / f.y)
        else:
            raise TypeError('Wrong type')
    
    def __neg__(self): # Negate Vector2
        return Vector2(-self.x, -self.y)
    
    def __abs__(self): # Absolute value of Vector2
        return Vector2(abs(self.x),abs(self.y))
    
    def __str__(self): # Print Vector2
        return str((self.x,self.y))
    
    def __repr__(self): # String representation of Vector2
        return str((self.x,self.y))
    
    def negative(self): # Negate Vector2
        return Vector2(-self.x, -self.y)
    
    def normalize(self): # Normalize Vector2
        x = self.x
        y = self.y
        l = sqrt(x*x + y*y) # Pythagoras
        return Vector2(x/l, y/l) if l else Vector2(0,0) # divide by zero error
    
    def Distance(self, other):
        return abs(sqrt(self.x*self.x + self.y*self.y) - sqrt(other.x*other.x + other.y*other.y))
    
    def Angle(self, other): # TODO
        x1 = self.x
        y1 = self.y
        x2 = other.x
        y2 = other.y
        return None
        #sin = x1 * y2 - x2 * y1
        #cos = x1 * x2 + y1 * y2
        #return atan2(sin, cos)
        #x3 = x1 + 1
        #y3 = y1
        #Al = atan2(y2 - y1, x2 - x1)
        #Bt = atan2(y3 - y1, x3 - x1)
        #w = (Bt - Al) % (2 * pi)
        #z = 180 * w / pi
        #return z
    
    def Sqrt(self):
        return Vector2(sqrt(self.x),sqrt(self.y))
    
    def Lerp(self, other, c): # Linear interpolation between two Vector2
        return Vector2(lerp(self.x,other.x,c), lerp(self.y,other.y,c))
    
    def Zero(): # Empty Vector2
        return Vector2(0,0)