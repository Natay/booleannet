"""
Testing the synchronous model
"""
import sys, unittest, string
from random import randint, choice
from itertools import *

import testbase

import boolean2
from boolean2 import util
            
class SyncTest( testbase.TestBase ):
    
    def test_cycle_detection( self):
        "Testing cycle detection"
        
        fprints = [
            [2, 2, 2, 2, 2],
            [1, 2, 3, 4, 5, 6, 7, 8, 9 ],
            [1, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3 ],
            [-3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 6, 1, 2 ],
        ]
        
        results = [
            (0, 1),
            (0, 0),
            (0, 4),
            (4, 6),
        ]
        
        for fp, res in zip(fprints, results):
            curr = util.detect_cycles( fp )
            self.EQ( res, curr )

    def test_initializer( self ):
        "Testing initializer"
        
        text = """
        A = False
        1: A* = A
        2: B* = A and B
        3: C* = not C
        """
        model  = boolean2.Model( mode='sync', text=text )
        model.initialize( missing= util.false, defaults=dict(A=True, B=True) )
        model.iterate( steps=10 )
        self.EQ( model.first.A, True )
        self.EQ( model.first.B, True )
        self.EQ( model.first.C, False )
        self.EQ( len(model.states), 11)

    def test_modeline( self ):
        "Basic operation"
        
        text = """
        A = B = True
        C = False
        1: A* = A
        2: B* = A and B
        3: C* = not C
        """
        model  = boolean2.Model( mode='sync', text=text )
        model.initialize()

        model.iterate( steps=5 )
        
        self.EQ( model.first.A, True )
        self.EQ( model.first.B, True )
        self.EQ( model.first.C, False )

        self.EQ( model.last.A, True )
        self.EQ( model.last.B, True )
        self.EQ( model.last.C, True )
        
    def test_random_rules( self ):
        """Testing rules (stress test)
        
        Generates lots of random rules and then compares the results 
        when executed in python and with the modeline
        """

        # valid nodes
        nodes  = string.ascii_uppercase[:]
        join = testbase.join
        #
        # Initializes a bunch of nodes to random values
        #
        values = [ choice( [True, False] ) for node in nodes ]
        init = [ '%s=%s' % (n,v) for n,v in zip(nodes, values) ]
        
        init_text = join(init) + '\n'

        operators = 'and or '.split()
        body  = []
  
        #    
        # for each node it attempts to build a complicated random expression like:
        #
        # (N or (J and B and M or not Z)) and not G
        #  
        # places nodes, operators and parentheses randomly (but syntactically correct)
        # then executes the rules in python but also with the modeline in synchronous 
        # mode and compares the outputs
        # 
        for node in nodes:
            
            # how many nodes per rule
            targets = [ choice( nodes ) for step in range( randint(2, 3) ) ]
            size = len( targets ) - 1

            # insert some parentheses
            if randint(1, 100) > 30:
                for i in range(2):
                    half = size/2
                    left, right = randint(0, int(half)), randint(int(half), size)
                    targets[left]  = '(' + targets[left]
                    targets[right] = targets[right] + ')'

            # add 'not' operators every once in a while
            if randint(1, 100) > 30:
                for steps in range( 2 ):
                    index = randint(0, size )
                    targets[index] = 'not ' + targets[index]
            
            # insert 'and/or' operators in between the nodes
            opers   = [ choice( operators ) for t in targets ][:-1]
            for index, oper in enumerate ( opers ):
                targets.insert( 2*index+1, oper)

            line = join( targets, sep= ' ')
            body.append( line )

        #
        # now that we have the expressions
        # generate python and modeline representations
        #
        py_text, bool_text = [], []
        newts = [ 'n%s' % node for node in nodes ]
        for line, newt, node in zip(body, newts, nodes):
            py_text.append( '%s = %s' % (newt, line) )    
            bool_text.append( '1: %s* = %s' % (node, line) )    

        # needs this to emulate synchronous updating
        py_text.append( join(nodes, sep=', ') + ' = ' + join( newts, sep=', ') )

        py_text   = join( py_text )
        bool_text = join( bool_text )
        full_text = init_text + py_text

        # execute the code in python for a number of steps
        # having too many steps is actually counterproductive as it falls into a steady state
        steps = 4
        exec (init_text)
        for i in range( steps ):
            exec ("py_text in locals()")
        
        # see the full text here
        #print (full_text)
        
        text = init_text + bool_text 

        test="""
        T = True
        Y = True
        T *= not not ((T) and Y)
        """

        test2 = """
        B = False
        E = False
        J = False
        Y = False
        B* = E or not not J or Y
        """

        test3 = """
        G = True
        H = False
        S = True
        H* = ((G) or S)
        """

        test4 = """
        K = False
        W = True
        B = True 
        B* = not ((K) or not W)
        """
        
        test5 = """
        K = False
        W = True
        B = True 
        X = True
        V = False
        S = True
        J = True
        B* = not ((K) or not W)
        K* = not ((X) or not V)
        W* = ((S)) and J
        """
        test6 = """
        N = True
        G = True
        A = True
        A* = ((N) and G)
        """


        tests = [
                 (test, 'TY', 'T = True; Y = True'),
                 (test2, 'BEJY', 'B = False; E = False; J = False; Y = False'),
                 (test3, 'GHS', 'G = True; H = False; S = True'),
                 (test4, 'BWK', 'B = True; W = True; K = False'),
                 (test5, 'KWBXVSJ', 'B = True; W = True; K = False; X = True;V = False;S = True;J = True'),
                 (test6, 'ANG', 'N = True; G = True; A = True'), 
                 (text, nodes, '')
                ]

        CURRENT_TEST = tests[-2]
        nodes = CURRENT_TEST[1]
        
        # Update local() namespace with correct nodes
        exec (CURRENT_TEST[2])

        print (CURRENT_TEST[0])

        # execute the code with the modeline
        states = testbase.get_states(mode='sync', text=CURRENT_TEST[0], steps=steps)
        last   = states[-1]
        
        # checks all states for equality with both methods
        print('\n')
        print(last)
        print('Node', 'oldval', 'newval')
     
        for attr in nodes:
            oldval = locals()[attr]
            newval = getattr(last, attr )
            print (attr, oldval, newval)
            self.EQ( oldval, newval )

def get_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase( SyncTest )
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner( verbosity=2 ).run( get_suite() )  
    

