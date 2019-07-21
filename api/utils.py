def ShowBoundingBoxPositions(imageHeight, imageWidth, box, rotation):
    """Calculate the bounding box surrounding an identified face.

    The calculation takes the image rotation into account.

    :param imageHeight: Height of entire image in pixels
    :param imageWidth: Width of entire image in pixels
    :param box: Dictionary containing bounding box data points
    :param rotation: Image orientation determined by Rekognition
    """

    # Calculate left and top points taking image rotation into account
    left = 0
    top = 0
    if rotation == 'ROTATE_0':
        left = imageWidth * box['Left']
        top = imageHeight * box['Top']

    if rotation == 'ROTATE_90':
        left = imageHeight * (1 - (box['Top'] + box['Height']))
        top = imageWidth * box['Left']

    if rotation == 'ROTATE_180':
        left = imageWidth - (imageWidth * (box['Left'] + box['Width']))
        top = imageHeight * (1 - (box['Top'] + box['Height']))

    if rotation == 'ROTATE_270':
        left = imageHeight * box['Top']
        top = imageWidth * (1 - box['Left'] - box['Width'])

    print('Bounding box of face:')
    print(f'  Left: {round(left)}, Top: {round(top)}, '
          f'Width: {round(imageWidth * box["Width"])}, '
          f'Height: {round(imageHeight * box["Height"])}')
