from app.models.database import Entity, Relation, get_db


def get_graph_data(document_id: int = None) -> dict:
    """获取知识图谱节点和边，用于可视化。"""
    db = get_db()
    try:
        entity_query = db.query(Entity)
        if document_id:
            entity_query = entity_query.filter(Entity.document_id == document_id)
        entities = entity_query.all()

        entity_ids = {e.id for e in entities}
        relation_query = db.query(Relation)
        if document_id:
            relation_query = relation_query.filter(Relation.document_id == document_id)
        relations = relation_query.all()

        nodes = [
            {
                "id": e.id,
                "name": e.name,
                "type": e.entity_type,
                "document_id": e.document_id,
            }
            for e in entities
        ]
        edges = [
            {
                "source": r.source_id,
                "target": r.target_id,
                "type": r.relation_type,
                "document_id": r.document_id,
            }
            for r in relations
            if r.source_id in entity_ids and r.target_id in entity_ids
        ]
        return {"nodes": nodes, "edges": edges}
    finally:
        db.close()


def search_entities(keyword: str, document_id: int = None, limit: int = 10) -> list[dict]:
    """按关键词搜索实体及其关联关系。"""
    db = get_db()
    try:
        query = db.query(Entity).filter(Entity.name.contains(keyword))
        if document_id:
            query = query.filter(Entity.document_id == document_id)
        entities = query.limit(limit).all()

        results = []
        for entity in entities:
            out_relations = (
                db.query(Relation, Entity)
                .join(Entity, Relation.target_id == Entity.id)
                .filter(Relation.source_id == entity.id)
                .all()
            )
            in_relations = (
                db.query(Relation, Entity)
                .join(Entity, Relation.source_id == Entity.id)
                .filter(Relation.target_id == entity.id)
                .all()
            )
            related = []
            for rel, target in out_relations:
                related.append(f"{entity.name} --[{rel.relation_type}]--> {target.name}")
            for rel, source in in_relations:
                related.append(f"{source.name} --[{rel.relation_type}]--> {entity.name}")
            results.append(
                {
                    "name": entity.name,
                    "type": entity.entity_type,
                    "document_id": entity.document_id,
                    "relations": related,
                }
            )
        return results
    finally:
        db.close()
