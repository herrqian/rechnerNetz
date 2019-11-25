import heapq


class Ergebnislist:

    def __init__(self, time, eventnumber):
        self.heapq = [(0, 'B', KundIn('A1')), (1, 'B', KundIn('B1')), (61, 'B', KundIn('B2')), (121, 'B', KundIn('B3')),
                      (181, 'B', KundIn('B4')), (200, 'B', KundIn('A2'))]
        self.time = time
        self.number = eventnumber
        self.bäcker = Station('Bäcker', 10)
        self.wursttheke = Station('Metzger', 30)
        self.käsetheke = Station('Käse', 60)
        self.kasse = Station('Kasse', 5)

    def pop(self):
        return heapq.heappop(self.heapq)

    def push(self, event):
        heapq.heappush(self.heapq, event)

    def start(self):
        mtime = 0
        eventnumber = 0
        a_id = 3
        b_id = 5
        while self.heapq or mtime >= self.time or eventnumber >= self.number:
            if mtime > 200:
                if mtime % 200 == 0:
                    self.push((mtime, 'B', KundIn('A' + str(a_id))))
                if (mtime - 1) % 60 == 0:
                    self.push((mtime, 'B', KundIn('B' + str(b_id))))
            time, event, customer = self.pop()
            if event == 'B':
                self.push((time + customer.tasks[0][0], 'A0', customer))
            elif event[0] == 'A':
                position = int(event[1])
                if customer.name[0] == 'A':
                    if position == 0:
                        self.customer_arrive(time, position, customer, self.bäcker)
                    elif position == 1:
                        self.customer_arrive(time, position, customer, self.wursttheke)
                    elif position == 2:
                        self.customer_arrive(time, position, customer, self.käsetheke)
                    else:
                        self.customer_arrive(time, position, customer, self.kasse)
                else:
                    if position == 0:
                        self.customer_arrive(time, position, customer, self.wursttheke)
                    elif position == 1:
                        self.customer_arrive(time, position, customer, self.kasse)
                    else:
                        self.customer_arrive(time, position, customer, self.bäcker)
            elif event[0] == 'L':
                position = int(event[1])
                if customer.name == 'T1':
                    if position == 0:
                        self.customer_leave(time, position, customer, self.bäcker)
                    elif position == 1:
                        self.customer_leave(time, position, customer, self.wursttheke)
                    elif position == 2:
                        self.customer_leave(time, position, customer, self.käsetheke)
                    else:
                        self.customer_leave(time, position, customer, self.kasse)
                else:
                    if position == 0:
                        self.customer_leave(time, position, customer, self.wursttheke)
                    elif position == 1:
                        self.customer_leave(time, position, customer, self.kasse)
                    else:
                        self.customer_leave(time, position, customer, self.bäcker)
            mtime += 1

    def customer_arrive(self, time, position, customer, station):
        if len(station.queue) >= customer.tasks[position][1]:
            if position < len(customer.tasks) - 1:
                self.push((time + customer.tasks[position + 1][0], 'A' + str(position + 1), customer))
            customer.action(time, 'dropped', station)
        else:
            station.action(time, 'adding', customer)
            station.queue.append((customer, position))
            if not station.is_working:
                station.is_working = True
                station.action(time, 'serving', customer)
                station.queue.pop(0)
                customer.action(time, 'Queueing', station)
                self.push((time + station.worktime * customer.tasks[position][2], 'L' + str(position), customer))
            else:
                customer.action(time, 'Queueing', station)

    def customer_leave(self, time, position, customer, station):
        customer.action(time, 'Finished', station)
        station.action(time, 'Finished', customer)
        if position < len(customer.tasks) - 1:
            self.push((time + customer.tasks[position + 1][0], 'A' + str(position + 1), customer))
            if station.queue:
                next_customer, n_position = station.queue.pop(0)
                station.action(time, 'serving', next_customer)
                self.push((time + next_customer.tasks[n_position][2] * station.worktime, 'V' + str(n_position),
                           next_customer))
            else:
                station.is_working = False


class Station:

    def __init__(self, name, worktime):
        self.name = name
        self.worktime = worktime
        self.queue = list()
        self.is_working = False

    def action(self, time, action, customer):
        with open('supermarkt_station.txt', mode="a") as f:
            text = str(time) + ':' + self.name + ' ' + action + ' customer ' + customer.name + '\n'
            f.write(text)
            f.flush()


class KundIn:

    def __init__(self, name):
        self.name = name
        if name[0] == "A":
            self.tasks = list([(10, 10, 10), (30, 10, 5), (45, 5, 3), (60, 20, 30)])
        elif name[0] == "B":
            self.tasks = list([(30, 5, 2), (30, 20, 3), (20, 20, 3)])
        else:
            return NotImplementedError

    def action(self, time, action, station):
        with open("supermarkt_customer.txt", mode="a") as f:
            text = str(time) + ':' + self.name + ' ' + action + ' at ' + station.name + '\n'
            f.write(text)
            f.flush()


if __name__ == "__main__":
    my_events = Ergebnislist(10000, 100000)
    my_events.start()
