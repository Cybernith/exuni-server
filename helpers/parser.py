from typing import List

from rest_framework import parsers


class NestedMultipartParser(parsers.MultiPartParser):

    @staticmethod
    def set_value(data, keys_string, value):
        keys_array = keys_string.split('[')
        for i in range(1, len(keys_array)):
            keys_array[i] = keys_array[i][:len(keys_array[i]) - 1]

        first_key = keys_array[0]

        if len(keys_array) == 1:
            data[first_key] = value
            return

        try:
            int(keys_array[1])
            data_chain = []
        except:
            data_chain = {}

        if first_key in data:
            data_chain = data[first_key]
        else:
            data[first_key] = data_chain

        for i in range(1, len(keys_array) - 1):
            key = keys_array[i]

            if isinstance(data_chain, List) and len(data_chain) > int(key):
                next_chain = data_chain[int(key)]
            elif key in data_chain:
                next_chain = data_chain[key]
            else:
                try:
                    int(keys_array[i + 1])
                    next_chain = []
                except:
                    next_chain = {}

            if isinstance(data_chain, List):
                key = int(key)
                if len(data_chain) <= key:
                    data_chain.append(next_chain)

            data_chain[key] = next_chain

            data_chain = data_chain[key]

        if isinstance(data_chain, List):
            data_chain.append(value)
        else:
            data_chain[keys_array[-1]] = value

    def parse(self, stream, media_type=None, parser_context=None):
        result = super().parse(stream=stream, media_type=media_type, parser_context=parser_context)

        is_nested = len([key for key, value in result.data.items() if '[' in key]) != 0

        if not is_nested:
            return result

        data = {}
        for key, value in result.data.items():
            self.set_value(data, key, value)
        for key, value in result.files.items():
            data.pop(key, None)
            self.set_value(data, key, value)
            self.set_value(data, key, value)
        return parsers.DataAndFiles(data, result.files)
