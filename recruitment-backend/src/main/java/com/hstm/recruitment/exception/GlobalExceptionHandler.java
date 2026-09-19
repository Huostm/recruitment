package com.hstm.recruitment.exception;

import com.hstm.recruitment.dto.ResultVO;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/**
 * @Author: recruitment-system
 * @Description: 全局异常处理
 */
@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(Exception.class)
    public ResultVO<String> handleException(Exception e) {
        log.error("系统异常", e);
        return ResultVO.error(e.getMessage());
    }

    @ExceptionHandler(RuntimeException.class)
    public ResultVO<String> handleRuntimeException(RuntimeException e) {
        log.error("运行时异常", e);
        return ResultVO.error(e.getMessage());
    }
}
