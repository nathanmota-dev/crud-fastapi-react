import { useState, useCallback } from "react";
import { Label } from "@radix-ui/react-label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Navigation } from "../navigation";
import { useDropzone } from "react-dropzone";

export const FormPage = () => {
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [files, setFiles] = useState<File[]>([]);

    const onDrop = useCallback((acceptedFiles: File[]) => {
        setFiles((prevFiles) => [...prevFiles, ...acceptedFiles]);
    }, []);

    const handleRemoveFile = (fileName: string) => {
        setFiles((prevFiles) => prevFiles.filter(file => file.name !== fileName));
    };

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();

        const formData = new FormData();
        formData.append("name", name);
        formData.append("email", email);
        files.forEach(file => {
            formData.append("files", file);
        });

        try {
            const response = await fetch("http://127.0.0.1:8000/upload", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                throw new Error("Network response was not ok");
            } else {
                const responseData = await response.json();
                console.log(responseData);
            }
        } catch (error) {
            console.error("There was a problem with the fetch operation:", error);
        }
    }

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/xml': ['.evtx']
        },
        multiple: true
    });

    return (
        <div>
            <Navigation />
            <div className="w-full h-screen flex justify-center items-center">
                <div className="border border-black p-20 rounded-3xl shadow-2xl">
                    <h1 className="text-3xl font-bold text-center">Formulário</h1>
                    <form className="gap-y-6" onSubmit={handleSubmit}>
                        <div className="pb-4">
                            <Label>Nome</Label>
                            <Input className="mt-1" type="text" value={name} onChange={(e) => setName(e.target.value)} />
                        </div>

                        <div className="pb-4">
                            <Label>E-mail</Label>
                            <Input className="mt-1" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
                        </div>

                        <div className="pb-4">
                            <Label className="pb-20">Envie seus arquivos Evtx</Label>
                            <div {...getRootProps()} style={{ border: '2px dashed #cccccc', padding: '20px', textAlign: 'center' }}>
                                <input {...getInputProps()} />
                                {isDragActive ? (
                                    <p>Solte os arquivos aqui ...</p>
                                ) : (
                                    <p>Arraste e solte arquivos aqui, ou clique para selecionar arquivos</p>
                                )}
                            </div>
                            {files.length > 0 && (
                                <div className="mt-4">
                                    <h4>Arquivos:</h4>
                                    <ul>
                                        {files.map(file => (
                                            <li key={file.name} className="flex justify-between items-center">
                                                <span>{file.name}</span>
                                                <button type="button" onClick={() => handleRemoveFile(file.name)}>Remover</button>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>

                        <div>
                            <Button type="submit" className="w-full">Enviar</Button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
}
