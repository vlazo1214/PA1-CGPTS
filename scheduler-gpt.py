# Implementation of SJF, FIFO, and RR using ChatGPT
# Member names: Vincent Lazo, Joaquin Castrillon, Dawn Martin, Christian Manuel

import sys
import heapq


class Process:
    def __init__(self, name, arrival, burst):
        self.name = name
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        self.start = -1
        self.finish = -1
        self.response = -1
        self.wait = 0
        self.turnaround = 0
        self.has_started = False

    def turnaround_time(self, finish):
        return finish - self.arrival

    def response_time(self, start):
        return max(start - self.arrival, 0)


def fcfs(processes, runtime, out):
    arrive_counter = 0
    finished_counter = 0
    running = Process("", 0, -1)

    order = processes.copy()
    order.sort(key=lambda p: p.arrival)

    waiting = []
    finished = []

    total_waiting_time = 0

    for i in range(runtime):
        while arrive_counter < len(order) and order[arrive_counter].arrival == i:
            proc = order[arrive_counter]
            waiting.append(proc)
            proc.wait = 0
            out.write(f"Time {i:4} : {proc.name} arrived\n")
            arrive_counter += 1

        if running.burst != -1:
            running.burst -= 1
            if running.burst == 0:
                out.write(f"Time {i:4} : {running.name} finished\n")
                running.finish = i + 1
                finished.append(running)
                finished_counter += 1
                total_waiting_time += running.wait
                running.burst = -1

        if running.burst == -1:
            if waiting:
                running = waiting.pop(0)
                if not running.has_started:
                    running.start = i
                    running.has_started = True
                    running.wait = i - running.arrival
                out.write(
                    f"Time {i:4} : {running.name} selected (burst {running.burst})\n")
            else:
                out.write(f"Time {i:4} : Idle\n")

    out.write(f"Finished at time {runtime}\n")

    for finished_proc in finished:
        for proc in processes:
            if finished_proc.name == proc.name:
                proc.turnaround = finished_proc.finish - proc.arrival

    calculate_metrics_fcfs(processes, out)
    return finished


def calculate_metrics_fcfs(processes, out):
    for process in processes:
        turnaround = process.turnaround_time(process.finish - 1)
        response = process.response_time(process.start)
        out.write(
            f"{process.name} wait {process.wait:4} turnaround {turnaround:4} response {response:4}\n")


def calculate_metrics_rr(processes, response_time_diff, out):
    total_turnaround_time = 0
    total_response_time = 0
    total_waiting_time = 0

    # Sort processes based on their names
    processes.sort(key=lambda p: p.name)

    for process in processes:
        turnaround = process.finish - process.arrival
        wait = turnaround - process.burst
        response = response_time_diff.pop(0)

        total_turnaround_time += turnaround
        total_response_time += response
        total_waiting_time += wait

        process.wait = wait
        process.turnaround = turnaround
        process.response = response

        out.write(
            f"{process.name} wait {wait:4} turnaround {turnaround:4} response {response:4}\n")

   # average_turnaround_time = total_turnaround_time / len(processes)
    #average_response_time = total_response_time / len(processes)
    #average_waiting_time = total_waiting_time / len(processes)

   # out.write(f"\nAverage Turnaround Time: {average_turnaround_time:.2f}")
   # out.write(f"Average Response Time: {average_response_time:.2f}")
   # out.write(f"Average Waiting Time: {average_waiting_time:.2f}")


def rr(processes, runtime, quantum, out):
    waiting = []
    finished = []
    current_time = 0
    selected_times = {process.name: [] for process in processes}

    # out.write(f"{len(processes)} processes")
    out.write("Using Round-Robin\n")
    out.write(f"Quantum {quantum}\n")

    # Sort processes based on arrival time
    processes.sort(key=lambda p: p.arrival)

    while processes or waiting:
        # Move the processes that arrive at the current time to waiting
        for process in processes[:]:
            if process.arrival <= current_time:
                waiting.append(process)
                processes.remove(process)
                if not process.has_started:
                    process.start = current_time
                    process.has_started = True
                    out.write(f"Time {current_time:4} : {process.name} arrived\n")

        if waiting:
            current_process = waiting.pop(0)
            if current_process.response == -1:
                current_process.response = current_time - current_process.arrival
                # Append the arrival, selected time, and response time to the list
                selected_times[current_process.name].append((current_process.arrival, current_time, current_process.response))
            out.write(
                f"Time {current_time:4} : {current_process.name} selected (burst {current_process.remaining})\n")

            if current_process.remaining > quantum:
                current_process.remaining -= quantum
                current_time += quantum
                # Reinsert the process to the end of the queue
                processes.append(current_process)
            else:
                current_time += current_process.remaining
                current_process.finish = current_time
                current_process.remaining = 0
                finished.append(current_process)
                out.write(
                    f"Time {current_time:4} : {current_process.name} finished\n")
        else:
            if processes or waiting:  # Check if there are processes left or waiting processes
                current_time += 1

    # out.write "Idle" with respective times at the end
    while current_time < runtime:
        out.write(f"Time {current_time:4} : Idle\n")
        current_time += 1

    out.write(f"Finished at time {runtime}\n")

    response_time_dif = []
    for process_name, times_list in selected_times.items():
        response_time_dif.extend([response for _, _, response in times_list])


    calculate_metrics_rr(finished, response_time_dif, out)
    return finished


def sjf(processes, runtime, out):
    arrive_counter = 0
    wait_counter = 0
    finished_counter = 0
    running = Process("", 0, -1)

    order = processes.copy()
    order.sort(key=lambda p: (p.arrival, p.burst))

    waiting = []
    finished = []
    burst_time = [0 for i in range(len(processes))]

    total_waiting_time = 0

    for i in range(runtime):
        while arrive_counter < len(order) and order[arrive_counter].arrival == i:
            proc = order[arrive_counter]
            waiting.append(proc)
            proc.wait = 0
            out.write(f"Time {i:4} : {proc.name} arrived\n")

            burst_time[processes.index(proc)] = proc.burst  # Written by human
            arrive_counter += 1
            wait_counter += 1

            if wait_counter > 1:
                waiting.sort(key=lambda p: p.burst)

        if running.burst != -1:
            running.burst -= 1
            if running.burst == 0:
                out.write(f"Time {i:4} : {running.name} finished\n")
                running.finish = i + 1
                finished.append(running)
                finished_counter += 1
                total_waiting_time += running.wait
                running.burst = -1
        if running.burst == -1:
            if wait_counter != 0:
                running = waiting.pop(0)
                if not running.has_started:
                    running.start = i
                    running.has_started = True

                    running.wait = i - running.arrival  # Update waiting time here
                out.write(
                    f"Time {i:4} : {running.name} selected (burst {running.burst})\n")
                wait_counter -= 1
            else:
                out.write(f"Time {i:4} : Idle\n")

        elif wait_counter != 0 and running.burst > waiting[0].burst:
            temp = running
            running = waiting.pop(0)
            waiting.append(temp)

            out.write(
                f"Time {i:4} : {running.name} selected (burst {running.burst})\n")

            waiting.sort(key=lambda p: p.burst)

    out.write(f"Finished at time {runtime}\n")

    for finished_proc in finished:
        for proc in processes:
            if finished_proc.name == proc.name:
                proc.turnaround = finished_proc.finish - proc.arrival

    calculate_metrics_sjf(processes, burst_time, out)
    return finished


def calculate_metrics_sjf(processes, burst_time, out):
    for process in processes:
        turnaround = process.turnaround_time(process.finish - 1)
        response = process.response_time(process.start)
        # Written by human
        wait = turnaround - burst_time[processes.index(process)]
        out.write(
            f"{process.name} wait {wait:4} turnaround {turnaround:4} response {response:4}\n")


def main():
    if len(sys.argv) != 2:
        out.write("Usage: scheduler-gpt.py <input file>\n")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = input_file.replace('.in', '.out')

    with open(output_file, 'w') as out:
        try:
            with open(input_file, 'r') as file:
                lines = file.readlines()

            process_count = int(lines[0].split()[1])
            run_for = int(lines[1].split()[1])
            algorithm = lines[2].split()[1]

            if algorithm == 'rr':
                try:
                    quantum = int(lines[3].split()[1])
                except IndexError:
                    out.write("Error: missing quantum for rr algorithm\n")
                    sys.exit(1)
                processes_data = lines[4:-1]
            else:
                quantum = None
                processes_data = lines[3:-1]

            processes = []
            for data in processes_data:
                parts = data.split()
                name = parts[2]
                arrival = int(parts[4])
                burst = int(parts[6])
                processes.append(Process(name, arrival, burst))

            out.write(f"{process_count} processes\n")
            if algorithm == 'sjf':
                out.write("Using preemptive Shortest Job First\n")
            elif algorithm == 'fcfs':
                out.write("Using First-Come First-Served\n")
            # else:  # elif algorithm == 'rr' and then add another else for edge cases
            #     out.write(
            #         f"Using {algorithm}{' Quantum ' + str(quantum) if algorithm == 'rr' and quantum else ''}")

            if algorithm == 'sjf':
                sjf(processes, run_for, out)
            elif algorithm == 'rr':
                # rr(processes, run_for, quantum)
                finished_processes = rr(processes, run_for, quantum, out)
            elif algorithm == 'fcfs':
                fcfs(processes, run_for, out)
        except FileNotFoundError:
            out.write(f"Error: file {input_file} not found\n")
            sys.exit(1)


if __name__ == "__main__":
    main()