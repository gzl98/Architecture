from project1.project1 import CPU

if __name__ == '__main__':

    cpu = CPU()
    with open('project1/codes.txt', 'r') as f:
        lines = f.readlines()

    for code in lines:
        cpu.run_code(code)
    cpu.show_memory()
