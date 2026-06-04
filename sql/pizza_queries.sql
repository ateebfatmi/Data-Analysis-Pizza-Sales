-- Determine the top 3 most ordered pizza types based on revenue for each pizza category.

SELECT
    category,
    pizza_name,
    revenue
FROM
(
    SELECT
        pizza_types.category,
        pizza_types.name AS pizza_name,
        ROUND(SUM(orders_details.quantity * pizzas.price), 2) AS revenue,
        DENSE_RANK() OVER (
            PARTITION BY pizza_types.category
            ORDER BY SUM(orders_details.quantity * pizzas.price) DESC
        ) AS rank_num
    FROM pizza_types
    JOIN pizzas
        ON pizza_types.pizza_type_id = pizzas.pizza_type_id
    JOIN orders_details
        ON pizzas.pizza_id = orders_details.pizza_id
    GROUP BY pizza_types.category, pizza_types.name
) ranked_pizzas
WHERE rank_num <= 3;