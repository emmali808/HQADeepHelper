package com.java.adds.service;

import com.java.adds.dao.KGDao;
import com.java.adds.entity.KGEntity;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Map;

/**
 * KG Service
 * @author QXL
 */
@Service
public class KGService {

    @Autowired
    private KGDao kgDao;

    /**
     * Upload Knowledge-Graph file
     * @param userId user's id
     * @return A KG ArrayList
     */
    public ArrayList<KGEntity> getKGListByUserId(Long userId) {
        return kgDao.getKGListByUserId(userId);
    }

    /**
     * Upload Knowledge-Graph
     * @param userId user id
     * @param kgName KG name
     * @param kgFilePath KG data file path
     * @return KG id
     */
    public Long uploadKG(Long userId, String kgName, String kgDesc, String kgFilePath) {
        Long kgId = kgDao.uploadKGFile(userId, kgName, kgDesc, kgFilePath);
        if (kgId >= 0) {
            kgDao.uploadKGData(kgFilePath, kgId);
            return kgId;
        } else {
            return -1L;
        }
    }

    /**
     * Get Knowledge-Graph by KG id
     * @param kgId KG id
     * @return KG data(partial): A String-Object Map format for D3
     */
    public Map<String, Object> getKGById(Long kgId) {
        Long nodeId = kgDao.getCentralNodeByKGId(kgId);
        if (nodeId < 0) {
            return kgDao.noDataFormat();
        } else {
            return kgDao.getNodeAndRelNodes(nodeId);
        }
    }

    /**
     * Get Knowledge-Graph node's relational nodes by node id (without this node)
     * @param nodeId KG node id
     * @return KG data(partial): A String-Object Map format for D3
     */
    public Map<String, Object> getRelNodes(Long nodeId) {
        return kgDao.getRelNodes(nodeId);
    }
}
