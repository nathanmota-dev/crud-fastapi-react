import { useState } from "react";
import { Label } from "@radix-ui/react-label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Navigation } from "../navigation";

export const FormPage = () => {

    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [file, setFile] = useState<File | null>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            setFile(e.target.files[0]);
        }
    }

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();

        const formData = new FormData();
        formData.append("name", name);
        formData.append("email", email);
        if (file) {
            formData.append("file", file);
        }

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
                            <Label className="pb-20" htmlFor="file">Envie seu arquivo Evtx</Label>
                            <Input className="mt-1" id="file" type="file" onChange={handleFileChange} />
                        </div>

                        <div>
                            <Button type="submit" className="w-full">Enviar</Button>
                        </div>

                    </form>
                </div>
            </div>
        </div>
    )
}