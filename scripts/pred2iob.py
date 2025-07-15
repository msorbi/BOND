#!/usr/bin/env python3
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Adapt predictions to hdsner")
    parser.add_argument('--input', type=str, required=True, help='Path to the input file')
    parser.add_argument('--output', type=str, required=True, help='Path to the output IOB file')
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    with open(args.input, "r") as fp:
        data = fp.read()
    data = data.strip().split("\n")
    data = [eval(x) for x in data]
    output = []
    for i in range(0, len(data), 3):
        seq = data[i:i+3]
        output.append("\n".join(" ".join(x) for x in zip(*seq)))
    output = "\n\n".join(output) + "\n"
    with open(args.output, "w") as fp:
        fp.write(output)

if __name__ == "__main__":
    main()
