class Data_Iterator:
    def __init__(self, data, page, per_page):
        self.data = data
        self.current_page = page
        self.items_per_page = per_page

    def __iter__(self):
        return self

    def __next__(self):
        if False:
            pass
        else:
            raise StopIteration
