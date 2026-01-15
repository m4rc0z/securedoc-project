package com.securedoc.backend;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;

@SpringBootApplication
@EnableAsync
public class SecureDocApplication {

	public static void main(String[] args) {
		System.setProperty("pdfbox.fontcache", "/tmp");
		SpringApplication.run(SecureDocApplication.class, args);
	}

}
