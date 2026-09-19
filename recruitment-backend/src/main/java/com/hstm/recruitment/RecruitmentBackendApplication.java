package com.hstm.recruitment;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.hstm.recruitment.mapper")
public class RecruitmentBackendApplication {

    public static void main(String[] args) {
        SpringApplication.run(RecruitmentBackendApplication.class, args);
    }

}
