/** /todos/{id} */
export interface TodosId {
    /** 待办事项ID，必填 */
    id: number;
    /** 是否已完成过滤，可选 */
    completed?: boolean;
}

/** /todos */
export interface Todos {
    /** 待办标题，必填 */
    title: string;
    /** 用户ID，必填 */
    userId: number;
    /** 是否已完成，可选 */
    completed?: boolean;
}

export {
    TodosId,
    Todos,
};
