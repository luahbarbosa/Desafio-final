-- Total de vendas por mês
SELECT DATE_TRUNC('month', data_pedido)::date AS mes,
       ROUND(SUM(valor_total)::numeric, 2)    AS total_vendas
FROM pedidos
GROUP BY 1
ORDER BY 1;

-- (b) Quantidade de pedidos por estado
SELECT c.estado, COUNT(*) AS qtd_pedidos
FROM pedidos p
JOIN clientes c ON c.id = p.cliente_id
GROUP BY c.estado
ORDER BY qtd_pedidos DESC;

-- (c) Pedidos divergentes
SELECT id, valor_total, valor_itens
FROM pedidos
WHERE divergente = TRUE
ORDER BY id;