import threading
import time
import random
from datetime import datetime


class ParkingLot:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.spaces = threading.Semaphore(capacity)
        self.entrance_open = threading.Event()
        self.entrance_open.set()
        self.lock = threading.Lock()
        self.occupied = 0
        self.parked_cars: set = set()

    def log(self, action: str, car_id: str = ""):
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        tag = f"[车{car_id}]" if car_id else "[管理员]"
        occ = f"(占用:{self.occupied}/{self.capacity})"
        print(f"{ts} {tag} {action} {occ}", flush=True)

    def enter(self, car_id: str):
        if not self.entrance_open.is_set():
            self.log("到达入口 → 入口已关闭，车辆离开", car_id)
            return

        if self.occupied >= self.capacity:
            self.log("到达入口 → 车位已满，排队等待...", car_id)

        acquired = self.spaces.acquire(timeout=2.0)
        if not acquired:
            if not self.entrance_open.is_set():
                self.log("等待中 → 入口已关闭，车辆离开", car_id)
            else:
                self.log("等待超时，车辆离开", car_id)
            return

        if not self.entrance_open.is_set():
            self.spaces.release()
            self.log("等待中 → 入口已关闭，车辆离开", car_id)
            return

        with self.lock:
            self.occupied += 1
            self.parked_cars.add(car_id)
        self.log("驶入停车场 ✓", car_id)

    def leave(self, car_id: str):
        with self.lock:
            if car_id not in self.parked_cars:
                self.log("尝试离开 → 未在场，无法离场", car_id)
                return
            self.parked_cars.remove(car_id)
            self.occupied -= 1
        self.spaces.release()
        self.log("驶离停车场，释放一个车位", car_id)

    def close_entrance(self):
        self.entrance_open.clear()
        self.log("关闭入口！不再允许新车进入")


def entrance_worker(lot: ParkingLot, car_ids: list):
    for cid in car_ids:
        time.sleep(random.uniform(0.3, 1.0))
        lot.enter(cid)


def exit_worker(lot: ParkingLot, ghost_cars: list, total_leaves: int):
    for cid in ghost_cars:
        time.sleep(random.uniform(0.3, 0.7))
        lot.leave(cid)

    for _ in range(total_leaves):
        time.sleep(random.uniform(0.8, 2.0))
        with lot.lock:
            if not lot.parked_cars:
                continue
            cid = random.choice(list(lot.parked_cars))
        lot.leave(cid)


def admin_worker(lot: ParkingLot, close_after: float):
    time.sleep(close_after)
    lot.close_entrance()


def main():
    capacity = 3
    num_cars = 8

    lot = ParkingLot(capacity)

    entering_cars = [f"A{i}" for i in range(1, num_cars + 1)]
    ghost_cars = [f"G{i}" for i in range(1, 3)]

    print("=" * 55, flush=True)
    print(f"  停车场信号量教学程序", flush=True)
    print(f"  总车位: {capacity}  模拟车辆: {num_cars}", flush=True)
    print(f"  信号量(Semaphore)初始值 = {capacity}", flush=True)
    print(f"  规则: acquire()获取车位 | release()释放车位", flush=True)
    print(f"  车位数不可能为负 → 信号量保证互斥安全", flush=True)
    print(f"  进场车辆集合追踪 → 未进场车辆无法离场", flush=True)
    print("=" * 55, flush=True)
    print(flush=True)

    t_entrance = threading.Thread(
        target=entrance_worker, args=(lot, entering_cars), name="EntranceThread"
    )
    t_exit = threading.Thread(
        target=exit_worker, args=(lot, ghost_cars, capacity + 3), name="ExitThread"
    )
    t_admin = threading.Thread(
        target=admin_worker, args=(lot, 8.0), name="AdminThread"
    )

    t_entrance.start()
    t_exit.start()
    t_admin.start()

    t_entrance.join()
    t_exit.join()
    t_admin.join()

    print(flush=True)
    print("=" * 55, flush=True)
    print(f"  模拟结束  最终占用: {lot.occupied}/{lot.capacity}", flush=True)
    print(f"  信号量保护: 车位数始终 >= 0", flush=True)
    print("=" * 55, flush=True)


if __name__ == "__main__":
    main()
