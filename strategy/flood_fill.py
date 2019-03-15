
def floodfill(matrix, pos):
    if matrix[pos.x][pos.y] in [0, -1]:
        matrix[pos.x][pos.y] = -100
        # recursively invoke flood fill on all surrounding cells:
        if pos.x > 0:
            pos.x = pos.x - 1
            floodfill(matrix, pos)
        if pos.x < len(matrix[pos.y]) - 1:
            pos.x = pos.x + 1
            floodfill(matrix, pos)
        if pos.y > 0:
            pos.y = pos.y - 1
            floodfill(matrix, pos)
        if pos.y < len(matrix) - 1:
            pos.y = pos.y + 1
            floodfill(matrix, pos)
    else:
        return
