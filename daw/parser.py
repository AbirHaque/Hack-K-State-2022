class Parser:
    def __init__(self):
        self.functions=['sin','cos']
        self.operators=['^','*','/','+','-']

    def is_number(self,token):
        try:
            temp=int(token)
            return True
        except:
            return False

    def shunting_yard(self, input_string):
        operator_stack=[]
        output_queue=[]
        for token in input_string:
            if self.is_number(token):
                output_queue.append(token)
            elif token in self.functions:
                operator_stack.append(token)
            elif token in self.operators:

                print("!")
            elif token == "(":
                operator_stack.append(token)
            elif token == ")":
                print("!")
 
        if operator_stack[-1] == "(":
            raise Exception("Error: Unbalanced parentheses.")
        else:
            while len(operator_stack)!=0:
                output_queue.append(operator_stack.pop())