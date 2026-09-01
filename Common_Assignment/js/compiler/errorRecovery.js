/**
 * ScopeLab - Error Recovery System
 * Implements Phrase-Level Recovery and Panic-Mode Synchronization
 */

export class RecoveryEvent {
    constructor(technique, title, description, line, column, actionTaken, syncToken = null) {
        this.id = 'rec_' + Math.random().toString(36).substr(2, 9);
        this.technique = technique; // 'Phrase-Level Recovery' | 'Panic Mode Recovery'
        this.title = title;
        this.description = description;
        this.line = line;
        this.column = column;
        this.actionTaken = actionTaken;
        this.syncToken = syncToken;
        this.timestamp = new Date();
    }
}

export class RecoveryManager {
    constructor() {
        this.events = [];
    }

    reset() {
        this.events = [];
    }

    recordPhraseLevel(title, description, line, column, actionTaken) {
        const event = new RecoveryEvent(
            'Phrase-Level Recovery',
            title,
            description,
            line,
            column,
            actionTaken
        );
        this.events.push(event);
        return event;
    }

    recordPanicMode(title, description, line, column, syncToken, skippedCount = 0) {
        const actionTaken = `Skipped ${skippedCount} token(s) until synchronization token '${syncToken}'. Resumed parsing at line ${line}.`;
        const event = new RecoveryEvent(
            'Panic Mode Recovery',
            title,
            description,
            line,
            column,
            actionTaken,
            syncToken
        );
        this.events.push(event);
        return event;
    }

    getEvents() {
        return this.events;
    }
}
