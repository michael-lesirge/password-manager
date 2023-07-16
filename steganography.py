# Thanks Computerphile. https://youtu.be/TWEXCYQKyDc

class Config:
    # TODO check file for any stop codes that might appear in it and change them or change stop code
    STOP_CODE = b''


def to_binary(data: bytes) -> str:
    return "".join(format(i, "08b") for i in data)


class InvalidPNGFile(Exception):
    pass


def get_png_body_position(image: bytes) -> tuple[int, int]:
    try:
        png_body_start = image.index(b'IDAT') + 4
    except:
        raise InvalidPNGFile("Invalid PNG file. Unable to find IDAT marker.")

    try:
        png_body_end = image.index(b'IEND')
    except InvalidPNGFile:
        raise Exception("Invalid PNG file. Unable to find IEND marker.")

    return png_body_start, png_body_end


def encode_image(base_png_image: bytes, secret_data: bytes) -> bytes:
    image = bytearray(base_png_image)

    secret_data_binary = to_binary(secret_data + Config.STOP_CODE)

    start_index, end_index = get_png_body_position(image)

    free_bytes = (end_index-start_index-len(to_binary(Config.STOP_CODE))) // 8
    if len(secret_data_binary) > free_bytes:
        raise Exception(
            f"Need bigger image to store all data. Currently have {free_bytes} free bytes,")

    for i, bit in enumerate(secret_data_binary):
        byte_index = end_index - i - 8
        # set last bit of byte to bit
        image[byte_index] = (image[byte_index] & 0b11111110) | int(bit, base=2)

    return bytes(image)


def decode_image(encoded_image: bytes) -> bytes:
    image = bytearray(encoded_image)

    start_index, end_index = get_png_body_position(image)
    byte_array = bytearray()
    stop_code = bytearray(Config.STOP_CODE)

    for byte_index in range(end_index, start_index, -8):
        byte = 0
        for bit_index in range(byte_index, byte_index-8, -1):
            # get last bit of byte by setting all other values to zero except last tone
            bit = image[bit_index] & 0b00000001
            # shift found byte left by one to make room for new bit on end. works since only end bit could be on in "bit"
            byte = (byte << 1) | bit
        if byte_array[-len(stop_code):] == stop_code:
            break
        byte_array.append(byte)
    else:
        raise Exception("No stop byte found")

    return bytes(byte_array)[1:-len(stop_code)]


def main() -> None:
    # TODO add subtracted image difference (Like shown in video)

    with open("steganography_images/example_starting_image.png", "rb") as file:
        image = file.read()

    in_string = "Super secret code"
    encoded_image = encode_image(image, in_string.encode())

    out_string = decode_image(encoded_image).decode()

    assert in_string == out_string, f"In and out strings not equal, {in_string=}, {out_string=}"

    print(out_string)


if __name__ == "__main__":
    main()
