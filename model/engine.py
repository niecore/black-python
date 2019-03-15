# snakes_alive = filter(lambda snake0: snake0["alive"] is True, snakes)
#
# move_options = [calculate_best_move(snake0, snakes, height, width, foods) for snake0 in snakes_alive]
#
# # Move head by adding a new body part at the start of the body array in the move direction
# for rated_options, snake0 in zip(move_options, snakes_alive):
#     fav_move = max(rated_options, key=rated_options.get)
#     snake0["body"].insert(0, get_new_position(get_snake_head(snake0), fav_move))
#
# # Reduce health
# for snake0 in snakes_alive:
#     snake0["health"] = snake0["health"] - 1
#
# # Check if the snake ate and adjust health
# # If the snake ate this turn, add a new body segment, underneath the current tail.
# # Remove eaten food
# for snake0 in snakes_alive:
#     if get_snake_head(snake0) in foods:
#         snake0["health"] = 100
#         snake0["body"].append = snake0["body"][:-1]
#         foods = filter(lambda food: food == get_snake_head(snake0), foods)
#
# # Remove the final body segment
# for snake0 in snakes_alive:
#     del snake0["body"][-1]
#
# # Check for snake death
# for snake0 in snakes_alive:
#     if wall_collusion(get_snake_head(snake0), height, width) or \
#             snake_collusion(get_snake_head(snake0), snakes_alive) or \
#             starved(snake0) or \
#             head_to_head_death(snake0, snakes_alive):
#         snake0["alive"] = False