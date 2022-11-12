from math import *
class Parser:
    def __init__(self):
        self.functions=['sin','cos','tan','ln','max','min']
        self.operators=['^','*','/','+','-']
        self.left_associative=['*','/','+','-']
        self.precedence={
            '^': 4,
            '*': 3,
            '/': 3,
            '+': 2,
            '-': 2
        }
        self.valid_variables=['t','a','f']

    def is_number(self,token):
        try:
            temp=float(token)
            return True
        except:
            return False
    def is_variable(self,token):
        return token in self.valid_variables

    def tokenize(self, string):
        string = string.replace(" ","").replace("("," ( ").replace(")"," ) ").replace("pi","3.141592653589793").replace(","," , ")
        for function in self.functions:
            string=string.replace(function," "+function+" ")
        for operator in self.operators:
            string=string.replace(operator," "+operator+" ")
        tokens = string.split(" ")
        for i in range(len(tokens)-1,-1,-1):
            if tokens[i]=="":
                tokens.pop(i)
        return tokens            

    def shunting_yard(self, input_string):
        operator_stack=[]
        output_queue=[]
        tokens=self.tokenize(input_string)
        for token in tokens:
            if token == ",":
                pass
            elif self.is_number(token) or self.is_variable(token):
                output_queue.append(token)
            elif token in self.functions:
                operator_stack.append(token)
            elif token in self.operators:
                while len(operator_stack)!=0 and (operator_stack[-1]!='(' \
                and (self.precedence[operator_stack[-1]]>self.precedence[token] \
                    or (self.precedence[operator_stack[-1]]==self.precedence[token] and token in self.left_associative))):
                    output_queue.append(operator_stack.pop())
                operator_stack.append(token)
            elif token == "(":
                operator_stack.append(token)
            elif token == ")":
                if len(operator_stack)==0:
                    raise Exception("Error: Mismatched parentheses.")
                while operator_stack[-1]!='(':
                    output_queue.append(operator_stack.pop())
                    if len(operator_stack)==0:
                        raise Exception("Error: Mismatched parentheses.")
                operator_stack.pop()#Discard left parenthesis
                if len(operator_stack)!=0 and operator_stack[-1] in self.functions:
                    output_queue.append(operator_stack.pop())
        if len(operator_stack)!=0 and operator_stack[-1] == "(":
            raise Exception("Error: Unbalanced parentheses.")
        else:
            while len(operator_stack)!=0:
                output_queue.append(operator_stack.pop())
        return output_queue

    def calculate(self,post_fix_queue):
        args = []
        for token in post_fix_queue:
            if self.is_number(token):
                args.append(float(token))
            elif token in self.functions:
                if token == 'sin':
                    args[-1]=sin(args[-1])
                elif token == 'cos':
                    args[-1]=cos(args[-1])
                elif token == 'tan':
                    args[-1]=tan(args[-1])
                elif token == 'ln':
                    args[-1]=log(args[-1])
                elif token == 'max':
                    args[-2]=args[-2] if args[-2]>args[-1] else args[-1]
                    args.pop()
                elif token == 'min':
                    args[-2]=args[-2] if args[-2]<args[-1] else args[-1]
                    args.pop()
            elif token in self.operators:
                if token == '^':
                    args[-2]=args[-2]**args[-1]
                    args.pop()
                elif token == '*':
                    args[-2]=args[-2]*args[-1]
                    args.pop()
                elif token == '/':
                    args[-2]=args[-2]/args[-1]
                    args.pop()
                elif token == '+':
                    args[-2]=args[-2]+args[-1]
                    args.pop()
                elif token == '-':
                    args[-2]=args[-2]-args[-1]
                    args.pop()
        return args[0]