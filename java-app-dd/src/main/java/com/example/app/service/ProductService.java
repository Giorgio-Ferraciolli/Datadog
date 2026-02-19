package com.example.app.service;

import com.example.app.model.Product;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

@Slf4j
@Service
public class ProductService {

    private final Map<Long, Product> productStore = new ConcurrentHashMap<>();
    private final AtomicLong idSequence = new AtomicLong(1);

    public ProductService() {
        seedProducts();
    }

    public List<Product> findAll() {
        log.info("Listando todos os produtos. Total: {}", productStore.size());
        return new ArrayList<>(productStore.values());
    }

    public Optional<Product> findById(Long id) {
        Optional<Product> product = Optional.ofNullable(productStore.get(id));
        if (product.isEmpty()) {
            log.warn("Produto com id={} não encontrado", id);
        }
        return product;
    }

    public Product create(Product product) {
        long newId = idSequence.getAndIncrement();
        product.setId(newId);
        productStore.put(newId, product);
        log.info("Produto criado: id={}, name={}", newId, product.getName());
        return product;
    }

    public Optional<Product> update(Long id, Product updated) {
        if (!productStore.containsKey(id)) {
            return Optional.empty();
        }
        updated.setId(id);
        productStore.put(id, updated);
        log.info("Produto atualizado: id={}", id);
        return Optional.of(updated);
    }

    public boolean delete(Long id) {
        Product removed = productStore.remove(id);
        if (removed != null) {
            log.info("Produto deletado: id={}", id);
            return true;
        }
        return false;
    }

    private void seedProducts() {
        List<Product> initial = List.of(
            Product.builder().name("Notebook Pro").description("Laptop de alta performance").price(5499.99).stock(10).build(),
            Product.builder().name("Teclado Mecânico").description("Switch Cherry MX Red").price(399.90).stock(50).build(),
            Product.builder().name("Monitor 4K").description("27 polegadas, 144Hz").price(2199.00).stock(20).build()
        );
        initial.forEach(this::create);
    }
}
