class Node:
    def __init__(self, key, val, prev=None, next_=None):
        self.key = key
        self.val = val
        self.prev = prev
        self.next_ = next_

    def __repr__(self):
        return str(self.val)


class LinkedList:
    def __init__(self):
        self.head = Node(None, "header")
        self.tail = Node(None, "tail")
        self.head.next_ = self.tail
        self.tail.prev = self.head
        self.size = 0

    def append(self, node):
        prev = self.tail.prev
        node.prev = prev
        node.next_ = prev.next_
        prev.next_ = node
        node.next_.prev = node
        self.size += 1

    def delete(self, node):
        prev = node.prev
        next_ = node.next_
        prev.next_, next_.prev = next_, prev
        self.size -= 1

    def delete_node_by_key(self, key) -> bool:
        node = self.head.next_
        while node != self.tail:
            if node.key == key:
                self.delete(node)
                return True
            node = node.next_
        return False

    def get_list(self):
        ret = []
        cur_node = self.head.next_
        while cur_node != self.tail:
            ret.append(cur_node)
            cur_node = cur_node.next_
        return ret

    def get_node_by_key(self, key):
        cur_node = self.head.next_
        while cur_node != self.tail:
            if cur_node.key == key:
                return cur_node
            cur_node = cur_node.next_
        return None


class HashMap:
    def __init__(self, capacity=16, load_factor=5):
        self.capacity = capacity
        self.load_factor = load_factor
        self.headers = [LinkedList() for _ in range(capacity)]

    def get_hash_key(self, key):
        return hash(key) & (self.capacity - 1)

    def _put(self, key, val):
        linked_list = self.headers[self.get_hash_key(key)]
        if linked_list.size >= self.capacity * self.load_factor:
            self.reset()
            linked_list = self.headers[self.get_hash_key(key)]
        node = linked_list.get_node_by_key(key)
        if node:
            node.val = val
        else:
            linked_list.append(Node(key, val))

    def get(self, key, default=None):
        linked_list = self.headers[self.get_hash_key(key)]
        node = linked_list.get_node_by_key(key)
        if node is None and default:
            return default
        return node

    def __getitem__(self, item):
        if self.get(item):
            return self.get(item)
        raise KeyError("无效的key")

    def __setitem__(self, key, value):
        self._put(key, value)

    def keys(self):
        for head in self.headers:
            for node in head.get_list():
                yield node.key

    def values(self):
        for head in self.headers:
            for node in head.get_list():
                yield node.val

    def items(self):
        for head in self.headers:
            for node in head.get_list():
                yield node.key, node.val

    def setdefault(self, key, default):
        if self.get(key):
            return default
        self._put(key, default)
        return True

    def delete(self, key) -> bool:
        linked_list = self.headers[self.get_hash_key(key)]
        return linked_list.delete_node_by_key(key)

    def reset(self):
        headers = [LinkedList() for _ in range(self.capacity * 2)]
        self.capacity = self.capacity * 2
        for linked_list in self.headers:
            nodes = linked_list.get_list()
            for node in nodes:
                hash_key = self.get_hash_key(node.key)
                linked_list_ = headers[hash_key]
                linked_list_.append(node)
        self.headers = headers


if __name__ == '__main__':
    # 创建字典
    m1 = HashMap()

    # 添加键值对
    m1["name"] = "马亚南"
    m1["age"] = 18

    # 获取键对应的值
    print(m1["name"], m1.get("age"))

    # 获取字典的容量
    # print("capacity", m1.capacity)
    # 1268不会扩容，1269自动扩容，1280是桶分配绝对均匀的情况，也即是说16*80=1280
    # for i in range(1269):
    #     m1[i] = i * 10
    # print("capacity", m1.capacity)

    # 删除元素
    print(m1.delete("name"), "删除成功")
    # print(m1["name"])  # 此语句会抛出KeyError错误
    print(m1.get("name", "默认值-哈哈哈"))

    # setdefault设置，跟python的实现等价
    name = m1.setdefault("name", "王五")
    print(name, "-setdefault")

    # keys
    for key in m1.keys():
        print(key)

    # values
    for val in m1.values():
        print(val)

    # items:
    for key, val in m1.items():
        print(key, val)

