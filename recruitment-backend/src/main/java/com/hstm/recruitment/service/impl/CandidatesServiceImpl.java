package com.hstm.recruitment.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.hstm.recruitment.entity.Candidates;
import com.hstm.recruitment.service.CandidatesService;
import com.hstm.recruitment.mapper.CandidatesMapper;
import org.springframework.stereotype.Service;

/**
* @author Administrator
* @description 针对表【candidates】的数据库操作Service实现
* @createDate 2026-09-04 12:20:20
*/
@Service
public class CandidatesServiceImpl extends ServiceImpl<CandidatesMapper, Candidates>
    implements CandidatesService{

}




