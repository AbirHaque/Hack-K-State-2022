from parser import Parser

parser = Parser()

'''
Tests are based off Wikipedia's page on the Shunting Yard algorithm:
https://en.wikipedia.org/wiki/Shunting_yard_algorithm
'''
tests = {
    '3 + 4':'3 4 + ',
    '3+4*2/(1-5)^2^3':'3 4 2 * 1 5 - 2 3 ^ ^ / + ',
    'sin(max(2,3)/3*pi)':'2 3 max 3 / 3.141592653589793 * sin ',
    '5':'5'
}
for test in list(tests.keys()):
    output_queue = parser.shunting_yard(test)
    post_fix=""
    for token in output_queue:
        post_fix+=(token+" ")
    if tests[test]!=post_fix:
        print("Error")
        print("Test:",test)
        print("Answer:",tests[test]+"|")
        print("Incorrect computation:",post_fix+"|")
    else:
        print("Success")
    print(parser.calculate(output_queue))